---
ticket: LP-0009
status: approved
created: 2026-10-17
approved: 2026-10-18
reviewer: Johnny Chang
---

# PRD: LINE Login with self-signup

Implements `LP-0009`, filed as `LP-0009-line-login.md` and listed in
[docs/issues/](../issues/README.md). Its folder follows its status. Behavior,
scope, and settled decisions live in the ticket and are not restated here.

## Before → After

### LINE sign-in

- **Before:** None (new). Google's flow is in `docs/modules/auth/index.md`
  § Sign-in flow.
- **After:**
  1. `login.html` shows the Google button, then a LINE button linking to
     `GET /auth/line?next=…`.
  2. `/auth/line` stores the validated `next` as `session['login_next']`.
     It pops `choose_account` and, if it was set, adds
     `disable_auto_login=true`. Authlib then redirects to LINE with `state`
     and `nonce`.
  3. LINE redirects to `GET /auth/line/callback`. Authlib checks `state`,
     exchanges the code at LINE's token endpoint, and verifies the ID token:
     an HS256 signature keyed by the channel secret, `iss`, `aud`, `exp`,
     `iat`, and `nonce`.
  4. `find_or_create_line_user(claims)` requires a non-empty `sub`. It looks
     the `sub` up in `users.line_user_id`. On a miss it inserts a new user,
     with `line_user_id = sub`, `email = None`, and a fresh random name as
     both `username` and `display_name` (BR-2).
  5. `create_session(user)` runs unchanged.
  6. 302 to `session.pop('login_next')`, re-validated as same-host, or the
     dashboard.

### Google sign-in

- **Before** (`services/auth.py:79-114`): `find_or_create_user` checks
  `email_verified`, then runs its own find-or-insert loop on `email`. It
  treats a `DuplicateKeyError` on `email` as a lost race.
- **After:** the behavior is unchanged. The find-or-insert loop moves into a
  shared `_find_or_create(field, value)`, which both providers call.
  `find_or_create_user` keeps its email checks and calls
  `_find_or_create('email', email)`. A new Google account also stores
  `line_user_id: None`.

### Logout flag

- **Before** (`routes/auth.py:35-43`, `:66-72`): logout sets
  `session['choose_account']`, and `google_login` pops it into
  `prompt=select_account`.
- **After:** `google_login` and `line_login` both pop it, so only the first
  sign-in started after logout uses it. LINE turns it into
  `disable_auto_login=true`.

### Startup

- **Before** (`app.py:20`, `:38-43`): `GOOGLE_CONFIG` names two required
  vars, and `create_app()` raises if either is missing.
- **After:** the tuple, renamed `OAUTH_CONFIG`, names four:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `LINE_CLIENT_ID`
  - `LINE_CLIENT_SECRET`

  After `oauth.init_app(app)`, `create_app()` sets the LINE client's
  verification key (BR-1).

### Index setup

- **Before** (`db/models.py:176-179`):
  `create_index('email', unique=True)`. A user without an email fails
  startup.
- **After:**
  1. `init_db()` drops `email_1` if its index information has no
     `partialFilterExpression`. This follows the `question_id_1` drop at
     `db/models.py:183`.
  2. It builds `email_1` unique, with
     `partialFilterExpression={'email': {'$type': 'string'}}`.
  3. It builds `line_user_id_1` unique, with
     `partialFilterExpression={'line_user_id': {'$type': 'string'}}`.

  On later boots the drop is skipped, and the build is a no-op.

### LP-0002-01 cleanup migration

- **Before** (`scripts/migrations/20261016_remove_username_only_users.py:15`):
  `FILTER = {'email': {'$exists': False}}`.
- **After:** the filter selects users with neither a string `email` nor a
  string `line_user_id`:

  ```python
  FILTER = {
      'email': {'$not': {'$type': 'string'}},
      'line_user_id': {'$not': {'$type': 'string'}},
  }
  ```

  It has not run on production (the `data-model.md` Change Log row for
  LP-0002-01 reads `pending: heroku`), so the change is safe.

## Route Contracts

### `GET /auth/login`

- **Auth:** none. Signed in → 302 to the dashboard (unchanged).
- **Request:** query `next`, optional.
- **Response:** 200 `login.html`. The Google button links to
  `/auth/google?next=<validated next>`, and below it the LINE button links to
  `/auth/line?next=<validated next>`.
- **Errors:** none.

### `GET /auth/line` (new)

- **Auth:** none. Signed in → 302 to the dashboard, with no LINE round trip.
- **Request:** query `next`, optional. Kept only if `_is_safe_redirect_url`
  passes, and otherwise replaced by the dashboard URL.
- **Response:** 302 to `https://access.line.me/oauth2/v2.1/authorize` with
  these parameters:
  - `response_type=code`
  - `client_id`
  - `redirect_uri`, set to
    `url_for('auth.line_callback', _external=True)`
  - `scope=openid`
  - `state`
  - `nonce`

  After an intentional logout, it also carries `disable_auto_login=true`,
  once. The session gains Authlib's state entry and `login_next`.
- **Errors:** none at request time. Missing config fails startup (BR-7).

### `GET /auth/line/callback` (new)

- **Auth:** none.
- **Request:** query `code` and `state`. When the user cancels, LINE instead
  sends `error`, `error_description`, and `state`.
- **Response:** 302 to the re-validated `login_next` or the dashboard, for an
  existing user and a new self-signup alike. The session holds `user_id`,
  `username`, and `display_name`, and `users.last_login` is set.
  `login_next` is popped.
- **Errors:** each case below → 302 `/auth/login`, with the flash
  「登入失敗，請重試」:
  - an `error` param;
  - a missing, mismatched, or reused `state`;
  - a token exchange failure;
  - an ID-token failure: a bad signature, `iss`, `aud`, `exp`, or `nonce`, a
    disallowed `alg`, or a missing `sub`;
  - an empty `sub` after verification.

  Authlib raises `OAuthError` (an `AuthlibBaseError`) or `joserfc`'s
  `JoseError`, which the route catches, as Google's callback does. In every
  error case there is no `users` write and no `user_id` in the session.
  Unlike Google, there is no unverified-email refusal, because LINE sends no
  email.

### `GET /auth/logout`

- Unchanged. The flag it leaves now serves both sign-in routes (BR-8).

### `GET /auth/google`, `GET /auth/google/callback`, `GET /auth/current`

- Unchanged.

## Data Changes

Each change goes through `schema-check` at implementation. Nothing here is
final until that skill writes `docs/modules/db/data-model.md`.

| Collection | Change | Existing documents | Migration |
| --- | --- | --- | --- |
| `users` | Add `line_user_id` (str or null). It holds the LINE `sub` for LINE accounts, and is null for Google accounts created after LP-0009. `UserModel` gains `line_user_id: Optional[str] = None`. | Google docs from before LP-0009 lack the field, which the partial index ignores. | none |
| `users` | `email` becomes optional: str for Google accounts, null for LINE accounts. `UserModel.email` becomes `Optional[str] = None`, moved after `display_name`. | Conform: every existing doc has a string email. | none |
| `users` | `email_1` rebuilt as unique partial, `{'email': {'$type': 'string'}}`. `init_db()` drops the old non-partial index once. | Build succeeds: the old index already enforced distinct string emails. | none (in `init_db()`) |
| `users` | Add `line_user_id_1`, unique partial, `{'line_user_id': {'$type': 'string'}}`. | No doc has a string `line_user_id` yet. | none |
| `users` | New insert writer: `find_or_create_line_user` on a first LINE sign-in, through the shared `_find_or_create`. | None affected. | none |
| `users` and the six per-user collections | The LP-0002-01 cleanup selects users with neither identity, so LINE accounts are never deleted. | None affected: not yet run on production. | `scripts/migrations/20261016_remove_username_only_users.py`, edited |

`tests/test_schema_drift.py` compares only index keys and uniqueness.
`schema-check` decides how `data-model.md` records the partial filters.

## Templates and UI Copy

- `templates/login.html`:
  - the subtitle changes;
  - a LINE button is added under the Google button, 12px below it, with the
    same 44px height, full width, and 4px radius.
- The LINE button follows LINE's login button guidelines:
  - base `#06C755`, with white text and icon;
  - hover adds a `#000000` overlay at 10% opacity, and press at 30%;
  - a `#000000` separator at 8% opacity sits between the icon and the text.

  The icon is the current LINE icon from LINE's official asset pack
  (`LINE_Login_Button_Image.zip`), unmodified, saved under `static/img/`.
  Focus uses the same `:focus-visible` outline as the Google button.

| Where | Current | After |
| --- | --- | --- |
| Login subtitle | 「請使用 Google 帳號登入」 | 「請使用 Google 或 LINE 帳號登入」 (proposed) |
| Google button | 「使用 Google 帳戶登入」 | Unchanged |
| LINE button | — | 「使用 LINE 帳號登入」 (proposed). LINE's zh-TW template text is 「與LINE連動」, and its guidelines allow custom text that clearly means "log in with LINE". |
| Login footer | 「第一次登入時會自動建立帳號」 | Unchanged |
| LINE refusal | — | 「登入失敗，請重試」 (reused) |
| New LINE account's name in the header | — | The random name, e.g. `learner-4f9k2a`, as for Google |

## LLM Prompts

None. Sign-in touches no prompt.

## Business Rules and Edge Cases

| ID | Rule or scenario | Expected behavior |
| --- | --- | --- |
| BR-1 | How the ID token is verified | `oauth.register('line', …)` without `server_metadata_url`. LINE's discovery advertises ES256, but web-login tokens are HS256 keyed by the channel secret. The registration sets: `authorize_url='https://access.line.me/oauth2/v2.1/authorize'`; `access_token_url='https://api.line.me/oauth2/v2.1/token'`; `issuer='https://access.line.me'`; `id_token_signing_alg_values_supported=['HS256']`; `client_kwargs={'scope': 'openid'}`. After `oauth.init_app`, `create_app()` sets `oauth.line.server_metadata['jwks'] = {'keys': [OctKey.import_key(secret).as_dict()]}` (`joserfc`, already an Authlib dependency). Authlib then checks the signature, `iss`, `aud`, `exp`, `iat`, and `nonce`, and refuses any other `alg`. Confirmed in a spike on 2026-10-17 against Authlib 1.9.1. |
| BR-2 | LINE self-signup | Inserts exactly one `users` doc: `line_user_id` = `sub`, unchanged (case-sensitive); `email: None`; `username` and `display_name` both `learner-` plus 6 hex characters; `created_at`; `last_login: None`. Then `create_session`. A second sign-in finds it. |
| BR-3 | A refused sign-in | Writes nothing: no `users` doc, no `last_login`, no `user_id` in the session. |
| BR-4 | LINE profile data | Never requested or written. The scope is `openid` alone. Any `name`, `picture`, or `email` claim is ignored. A sign-in never overwrites `username` or `display_name`. |
| BR-5 | No account linking | A LINE sign-in looks up only `line_user_id`, and a Google sign-in only `email`. Neither reads or writes the other provider's accounts. |
| BR-6 | `next` | Validated on the way in and again on the way out, with the same `_safe_next` and `login_next` Google uses. |
| BR-7 | Missing `LINE_CLIENT_ID` or `LINE_CLIENT_SECRET` | `create_app()` raises at startup, naming the missing var. Tests set dummy values. |
| BR-8 | Logout flag | The one-time `choose_account` flag is popped by whichever of `/auth/google` and `/auth/line` runs first after logout. LINE sends `disable_auto_login=true`, and Google sends `prompt=select_account`. |
| BR-9 | Heroku scheme | The existing `ProxyFix(x_proto=1)` makes the LINE `redirect_uri` `https://` too. |
| BR-10 | Identity uniqueness | `email_1` and `line_user_id_1` are unique over string values only. Nulls and missing fields never clash. |
| E-1 | The user cancels on LINE's screen | LINE redirects with `error=access_denied` → 「登入失敗，請重試」. |
| E-2 | The callback is replayed or opened directly | Authlib finds no state → 「登入失敗，請重試」. |
| E-3 | Two first sign-ins race on the same new `sub` | The losing insert hits `line_user_id_1`'s `DuplicateKeyError`, re-reads, and uses the winner's doc. |
| E-4 | The random name clashes with an existing `username` | Redraw, up to 5 tries. This is the shared `_find_or_create`, unchanged from Google. |
| E-5 | Already signed in, opens `/auth/line` | 302 to the dashboard. |
| E-6 | The same person signs in with Google and with LINE | Two accounts, with separate progress (BR-5). |
| E-7 | The channel is moved to another LINE provider | Every `sub` changes, and every LINE learner becomes a new account. The auth module doc's Operations section forbids the move. |
| E-8 | The channel is still "Developing" | Only channel admins and testers can sign in. Rollout step 5 publishes it. |
| E-9 | Opened inside LINE's in-app browser | LINE may sign in without a prompt. That is a normal sign-in. LIFF is out of scope. |

## Test Plan

LINE is never called. The service tests stub
`oauth.line.authorize_access_token` to return `{'userinfo': claims}`.

The ID-token tests stub only `oauth.line.fetch_access_token`. They return an
`id_token` signed locally with HS256 and `app.config['LINE_CLIENT_SECRET']`,
so Authlib's real verification runs. The state and `?error=` tests use real
Authlib, which refuses before any network call.

Test env defaults are `LINE_CLIENT_ID=1234567890` and
`LINE_CLIENT_SECRET=test-line-channel-secret`. The secret is at least 14
bytes, to avoid joserfc's key-size warning. OpenRouter is not involved.

- `tests/test_auth.py`
  - New `sub` → 302 to the dashboard. One new doc: `line_user_id` set,
    `email` None, `username == display_name` matching
    `^learner-[0-9a-f]{6}$`, and `last_login` set. `session['user_id']` is
    its `_id`. A second sign-in → the same `_id`, and the count is
    unchanged.
  - Existing LINE user, with a `name` claim present → a session for that
    doc, `last_login` set, and `display_name` unchanged.
  - Google user `alice` exists, then a LINE sign-in → the new LINE doc only.
    `alice` is unchanged, and the count is 2.
  - Two LINE signups with different `sub`s, then one Google signup → three
    docs, with no `DuplicateKeyError` on null `email` or null
    `line_user_id`.
  - Same-`sub` race: the lookup is stubbed to miss once while the doc
    already exists → no second doc, and the session holds the existing
    `_id`.
  - Real HS256 token → signs in.
  - Each bad token → 「登入失敗，請重試」, and nothing is written:
    - signed with another secret;
    - wrong `aud`;
    - wrong `iss`;
    - expired;
    - wrong `nonce`;
    - `alg` HS384;
    - no `sub`.
  - `?error=access_denied`, and an unknown `state` →
    「登入失敗，請重試」.
  - `GET /auth/line` with `X-Forwarded-Proto: https` → the location host is
    `access.line.me`, and:
    - `scope=openid`;
    - a `nonce` is present;
    - `redirect_uri` starts with `https://`;
    - there is no `disable_auto_login`.
  - Logout, then `GET /auth/line` → `disable_auto_login=true`. A second
    start → absent.
  - Logout, then `GET /auth/google` (which takes the flag), then
    `GET /auth/line` → no `disable_auto_login`.
  - `GET /auth/line?next=https://evil.example` → the callback lands on the
    dashboard. `next=/laws` → lands on `/laws`.
  - Signed in, `GET /auth/line` → 302 to the dashboard.
  - The startup test (D29) is parametrized over all four vars, adding
    `LINE_CLIENT_ID` and `LINE_CLIENT_SECRET`.
  - `GET /auth/login` → both hrefs present, the Google href before the
    LINE href.
  - Every existing Google test passes unchanged.
- `tests/test_migrations.py`
  - Seed `users` with a non-partial unique `email_1` and two Google docs,
    then run `init_db()`. `email_1` now has the partial filter, both docs
    remain, and `line_user_id_1` exists. A second `init_db()` changes
    nothing.
  - Seed a username-only user, a Google user, and a LINE user
    (`email: None`), each with documents in all six per-user collections.
    `apply` deletes only the username-only user and their documents. The
    LINE user and their documents remain.
- `tests/test_app.py`: add `LINE_CLIENT_ID` and `LINE_CLIENT_SECRET` via
  `os.environ.setdefault`, next to the Google ones.
- `tests/test_schema_drift.py`: passes once `data-model.md` lists
  `line_user_id` and `line_user_id_1`.

## Rollout and Migration

This ticket runs the production rollout (ticket Settled Decisions).

1. In the LINE Developers Console, pick the provider the channel will live
   under for good (E-7). Create a LINE Login channel, app type "Web app".
   Do not apply for email permission. On the LINE Login tab, register these
   callback URLs, one per line:
   - `http://localhost:5000/auth/line/callback`
   - `http://localhost:5001/auth/line/callback`
   - `https://law-pass-5ae90190d253.herokuapp.com/auth/line/callback`
2. Put the channel's "Channel ID" and "Channel secret" in the local `.env`
   as `LINE_CLIENT_ID` and `LINE_CLIENT_SECRET`. Add both to `.env.example`
   with placeholders.
3. Verify locally while the channel is still "Developing". The user's LINE
   account is a channel admin, so it can sign in.
4. Before merging to `main`:
   `heroku config:set LINE_CLIENT_ID=… LINE_CLIENT_SECRET=… -a law-pass`.
   The running release ignores them. Without them, the new release's
   `create_app()` raises and the dyno crashes.
5. Publish the channel ("Developing" → "Published"), so any LINE user can
   sign in. Doing this before the deploy is harmless: no button links to
   LINE yet.
6. Merge to `main`. CI runs, then Heroku auto-deploys. At boot, `init_db()`
   drops the old `email_1` and builds the partial `email_1` and
   `line_user_id_1`.
   - `schema-check` preflight: every production `users` doc has a distinct
     string email. The old unique index already guarantees this.
7. Smoke test on Heroku. The LINE test account signs itself up through the
   `https://` callback, the header shows `learner-…`, and a second sign-in
   reuses the account. Fill the `data-model.md` Change Log `Ran` cell.

Rollback: `heroku releases:rollback -a law-pass`. The previous release runs
`create_index('email', unique=True)`. That conflicts with the partial
`email_1` of the same name, so drop `email_1` in Atlas first. Even then, the
old non-partial index cannot be built once two or more LINE accounts exist,
because their null emails clash. So:

- a rollback is safe only until the second LINE signup;
- after that, fix forward. Deleting the LINE accounts is the only way back,
  and it needs the user's say-so.

No data is lost by rolling back before that point.

## Implementation Order

1. Schema via `schema-check`:
   - `UserModel`: `email` becomes optional, and `line_user_id` is added;
   - in `init_db()`, the `email_1` rebuild and `line_user_id_1`;
   - the narrowed LP-0002-01 migration filter;
   - the `data-model.md` update;
   - the `tests/test_migrations.py` cases.

   Google sign-in is untouched, so `pytest` stays green.
2. Move the find-or-insert loop into `_find_or_create(field, value)`.
   `find_or_create_user` calls it with `'email'`, and the Google tests stay
   green.
3. Config:
   - `OAUTH_CONFIG` with the LINE vars;
   - the `oauth.register('line', …)` registration;
   - the `jwks` set in `create_app()`;
   - the `.env.example` entries;
   - the test env defaults in `tests/test_auth.py` and `tests/test_app.py`;
   - the parametrized startup test.
4. `find_or_create_line_user`, `GET /auth/line`,
   `GET /auth/line/callback`, the shared logout flag, and their tests.
5. `login.html`: the subtitle, the LINE button with the official icon in
   `static/img/`, and the login page test.
6. Run the app locally against a local MongoDB with the real LINE channel
   (Rollout steps 1–3). The LINE test account signs itself up and signs in
   again, and after logout LINE shows its login screen.
7. Production: Rollout steps 4–7.
