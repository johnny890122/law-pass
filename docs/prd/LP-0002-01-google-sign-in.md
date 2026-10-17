---
ticket: LP-0002-01
status: draft
created: 2026-10-16
approved:
reviewer:
---

# PRD: Google sign-in with self-signup

Implements `LP-0002-01`, filed as `LP-0002-01-google-sign-in.md` and listed in
[docs/issues/](../issues/README.md). Its folder follows its status. Behavior,
scope, and settled decisions live in the ticket and are not restated here.

Revised on 2026-10-17 for self-signup. The invite-only version was approved
on 2026-10-16 and is superseded. Revised again on 2026-10-17 to remove
console account creation (`scripts/add_user.py` is deleted) and to move the
production rollout to `LP-0007`. The self-signup version approved that day
is superseded.

## Before → After

### Sign-in

- **Before** (`routes/auth.py:30-55`, `services/auth.py:59-89`; no
  `docs/modules/auth/` yet):
  1. `login.html` posts `username` and `next` to `POST /auth/login`.
  2. `validate_user` runs `users.find_one({'username': username})`.
  3. No match → flash 「用戶名稱不存在，請聯繫管理員」 → 302 `/auth/login`.
  4. `create_session` sets `user_id`, `username`, `display_name` in the
     session and `$set`s `users.last_login`.
  5. 302 to `next` (same-host only) or the dashboard.
- **After:**
  1. `login.html` links to `GET /auth/google?next=…`.
  2. The route stores the validated `next` as `session['login_next']`, and
     Authlib redirects to Google with `state` and `nonce`.
  3. Google redirects to `GET /auth/google/callback`. Authlib checks `state`,
     exchanges the code, and verifies the ID token (signature, `iss`, `aud`,
     `exp`, `nonce`).
  4. `email_verified` must be true and `email` non-empty. Otherwise flash
     「此 Google 帳號的電子郵件尚未驗證，無法登入」 → 302 `/auth/login`, and
     nothing is written.
  5. `find_or_create_user(claims)` looks up the lowercased, stripped email in
     `users.email`. On a miss it inserts a new user, the self-signup:
     `asdict(UserModel(email, username=name, display_name=name))`, where
     `name` is a fresh random name (BR-2).
  6. `create_session(user)` runs unchanged.
  7. 302 to `session.pop('login_next')`, re-validated as same-host, or the
     dashboard.

### Provisioning

- **Before** (`scripts/add_user.py:19-56`, `:105-128`):
  `add_user.py <username> <display_name>` rejects an existing username and
  inserts `asdict(UserModel)`. `--list` shows username, display name, created,
  and last login.
- **After:** none. `scripts/add_user.py` is deleted, including `--list`,
  along with its test. Every account comes from self-signup (BR-2). Admins
  view and edit users in Atlas.

### Cutover cleanup

- **Before:** None (new).
- **After:** a one-off migration deletes every `users` document without an
  `email`, plus every document keyed on those `_id`s in the six per-user
  collections.

## Route Contracts

### `GET /auth/login`

- **Auth:** none. Signed in → 302 to the dashboard (unchanged).
- **Request:** query `next`, optional.
- **Response:** 200 `login.html`, with the Google button's href set to
  `/auth/google?next=<validated next>`.
- **Errors:** none.

### `POST /auth/login`

- **Removed.** The route answers 405 because `GET /auth/login` still exists.
  No session is created.

### `GET /auth/google` (new)

- **Auth:** none. Signed in → 302 to the dashboard.
- **Request:** query `next`, optional. Kept only if `_is_safe_redirect_url`
  passes, and otherwise replaced by the dashboard URL.
- **Response:** 302 to Google's `authorization_endpoint` with
  `response_type=code`, `client_id`, `scope=openid email`, `state`, `nonce`,
  and `redirect_uri` set to `url_for('auth.google_callback', _external=True)`.
  The session gains Authlib's state entry and `login_next`.
- **Errors:** none at request time. Missing config fails startup (BR-7).

### `GET /auth/google/callback` (new)

- **Auth:** none.
- **Request:** query `code` and `state`, or `error` when the user cancels.
- **Response:** 302 to the re-validated `login_next` or the dashboard, for an
  existing user and a new self-signup alike. The session holds `user_id`,
  `username`, and `display_name`, and `users.last_login` is set.
  `login_next` is popped.
- **Errors:**
  - `error` param, state missing, mismatched, or reused, or a token or
    ID-token failure → 302 `/auth/login`, flash 「登入失敗，請重試」. Authlib
    raises `OAuthError` for the first group and the token exchange. ID-token
    verification raises `joserfc`'s `JoseError` in Authlib 1.9, so the route
    catches both.
  - `email_verified` not true, or no `email` claim → 302 `/auth/login`, flash
    「此 Google 帳號的電子郵件尚未驗證，無法登入」.
  - In every error case, no `users` write and no `user_id` in the session.

### `GET /auth/logout`, `GET /auth/current`

- Unchanged.

## Data Changes

Each change goes through `schema-check` at implementation. Nothing here is
final until that skill writes `docs/modules/db/data-model.md`.

| Collection | Change | Existing documents | Migration |
| --- | --- | --- | --- |
| `users` | Add `email` (str, required, stored lowercased). `UserModel` gains `email: str` before the defaulted fields. `username` becomes a stored label, not a login credential, and keeps `username_1`. | Username-only users are deleted, not backfilled. | `scripts/migrations/20261016_remove_username_only_users.py` |
| `users` | Add unique index `email_1` `[("email", 1)]` in `init_db()`, with no `try/except`. | After the migration, every document has a distinct email. Preflight on production before deploy. | Same script |
| `users` | `GET /auth/google/callback` becomes the only insert writer: it inserts `asdict(UserModel)` on a first sign-in, with `username` and `display_name` both set to one random name. `scripts/add_user.py`, the old insert writer, is deleted. No new field. | None affected. | None |
| `user_progress`, `user_law_stars`, `user_law_stats`, `user_question_stars`, `user_daily_stats`, `sessions` | Documents whose `user_id` is a deleted user's `_id` are deleted. No shape change. | Those documents only. | Migration script |

Migration contract:

- Selects `users` with `{"email": {"$exists": False}}`, then deletes their
  per-user documents first, and the `users` documents last. A crash midway
  leaves the user in place, so a rerun finishes the job.
- Dry-run by default: prints per-collection counts. Deletes only with
  `--apply`. Idempotent.
- Exposes `migrate(database, apply: bool) -> dict` of counts, so the test can
  call it without argparse.

## Templates and UI Copy

- `templates/login.html`: remove the form (`:155-174`) and its script
  (`:181-193`). Add one link-styled button to
  `{{ url_for('auth.google_login', next=next_url) }}`, with the Google "G"
  mark per Google's sign-in branding guidelines. Keep the flash block.
  Change the footer.

| Where | Current | After |
| --- | --- | --- |
| Login subtitle | 「請輸入您的用戶名稱登入」 | 「請使用 Google 帳號登入」 (proposed) |
| Login button | 「登入」 | 「使用 Google 帳戶登入」 (proposed; Google's zh-TW string) |
| Login footer | 「如果您沒有帳號，請聯繫管理員」 | 「第一次登入時會自動建立帳號」 (proposed) |
| Unverified email | 「用戶名稱不存在，請聯繫管理員」 | 「此 Google 帳號的電子郵件尚未驗證，無法登入」 (proposed) |
| OAuth failure or cancel | — | 「登入失敗，請重試」 (proposed) |
| Empty username (route and JS) | 「請輸入用戶名稱」 | Removed |
| Logout | 「已登出」 | Unchanged |
| New account's name in the header | — | The random name, e.g. `learner-4f9k2a`, until onboarding (`LP-0002-02`) changes it |
| `add_user.py` messages | 「❌ 錯誤：用戶名稱 '{username}' 已存在」 and the rest | Removed with the script |

## LLM Prompts

None. Sign-in touches no prompt.

## Business Rules and Edge Cases

| ID | Rule or scenario | Expected behavior |
| --- | --- | --- |
| BR-1 | Who gets a session | Any ID token with `email_verified: true` and a non-empty `email`. The lowercased email is matched against `users.email`, and a miss is a self-signup. |
| BR-2 | Self-signup | Inserts exactly one `users` doc: lowercased `email`; `username` and `display_name` both `learner-` plus 6 hex characters from `secrets.token_hex(3)`; `created_at`; `last_login: None`. Then `create_session`. A second sign-in finds it. |
| BR-3 | A refused sign-in | Unverified email or OAuth failure. Writes nothing: no `users` doc, no `last_login`, no `user_id` in the session. |
| BR-4 | Google profile data | Never requested or written. Scope is `openid email`. A sign-in never overwrites `username` or `display_name`, whether the signup or onboarding set them. |
| BR-5 | `next` | Validated on the way in and again on the way out. A foreign host falls back to the dashboard. |
| BR-6 | Username login | Gone in every environment. `POST /auth/login` → 405. |
| BR-7 | Missing `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET` | `create_app()` raises at startup, naming the missing var. Tests set dummy values. |
| BR-8 | Heroku scheme | `ProxyFix(x_proto=1)` wraps `app.wsgi_app`, so `redirect_uri` is `https://` behind Heroku's router. |
| BR-9 | Production gating | Enforced by deploy order only, with no code switch. This code deploys after `LP-0002-05` lands (Rollout step 7, run by `LP-0007`). |
| E-1 | The user cancels on Google's consent screen | 「登入失敗，請重試」. |
| E-2 | The callback is replayed or opened directly | Authlib finds no state → 「登入失敗，請重試」. |
| E-3 | Email case differs (`Alice@Gmail.com`) | Matches after lowercasing. No second account. |
| E-4 | The user's Google email changed | Signs up as a new account. The old one stays, unlinked, because account linking is out of scope. |
| E-5 | Already signed in, opens `/auth/google` | 302 to the dashboard, with no Google round trip. |
| E-6 | Two tabs start sign-in | Authlib keys state per value, so both callbacks succeed once each. |
| E-7 | Two first sign-ins race on the same new email | The insert that loses hits `email_1`'s `DuplicateKeyError`, re-reads, and uses the winner's doc. One account, two sessions. |
| E-8 | The random name clashes with an existing `username` | `username_1`'s `DuplicateKeyError` → draw a new name and retry, up to 5 tries. Five clashes in a row in a 16.7M space is practically unreachable, and surfaces as a 500. |

## Test Plan

Google is never called. `oauth.google.load_server_metadata` is
monkeypatched to a static discovery dict, and
`oauth.google.authorize_access_token` to return a token whose `userinfo`
holds the claims. The state and `?error=` tests use real Authlib, which
refuses before any network call. OpenRouter is not involved.

- `tests/test_auth.py`
  - Provisioned, verified email → 302 to the dashboard,
    `session['user_id']` equals the provisioned `_id`, `last_login` is set,
    and `display_name` is unchanged with a differing `name` claim.
  - New verified email (mixed case) → 302 to the dashboard. One new `users`
    doc: lowercased email, `username == display_name` matching
    `^learner-[0-9a-f]{6}$`, and `last_login` set. `session['user_id']` is
    its `_id`. A second sign-in → the same `_id`, and the count is unchanged.
  - Random-name clash: the name generator is stubbed to return an existing
    `username` first → the second name is used, and one doc is added.
  - Same-email race: the email lookup is stubbed to miss once while the doc
    already exists → no second doc, and the session holds the existing `_id`.
  - `email_verified: false`, or no `email_verified` claim → 302
    `/auth/login` with the unverified copy, and nothing is written.
  - Callback with an unknown `state` (unmocked) → 「登入失敗，請重試」.
  - Callback with `?error=access_denied` → 「登入失敗，請重試」.
  - `POST /auth/login` with `username=alice` → 405, no `user_id`.
  - `GET /auth/google?next=https://evil.example` → callback lands on the
    dashboard. `next=/laws` → lands on `/laws`.
  - `GET /auth/google` with `X-Forwarded-Proto: https` → the `redirect_uri`
    query param starts with `https://`, and `scope` is `openid email`.
  - The `add_user()` test is deleted with the script.
- `tests/test_migrations.py`
  - Seed a username-only user and an emailed user, each with one document
    in all six per-user collections. A dry run deletes nothing. `apply`
    deletes only the username-only user and their six docs. A second
    `apply` reports zero.
- `tests/test_app.py`: `GET /auth/login` → 200 still holds. Set
  `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` via `os.environ.setdefault`
  next to `SECRET_KEY`.
- `tests/test_schema_drift.py`: passes once `data-model.md` lists `email` and
  `email_1`.

## Rollout and Migration

This rollout runs as its own ticket, `LP-0007`. Prerequisites: `LP-0003`
(the new law-pass Heroku app) and `LP-0002-05` (the per-user daily grading
cap) have both landed. Until then this code runs locally only (BR-9).

1. In Google Cloud Console, create a Web application OAuth client. Register
   `http://localhost:5000/auth/google/callback`,
   `http://localhost:5001/auth/google/callback` (for Macs where AirPlay
   Receiver holds port 5000), and
   `https://<app>.herokuapp.com/auth/google/callback`. Publish the consent
   screen to "In production", which basic `openid email` scopes allow without
   verification. Otherwise "Testing" mode adds a second allowlist.
2. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` on Heroku and in the
   local `.env`.
3. Before `--apply`, `mongodump` the seven affected collections from
   production. This is the only way back.
4. From a local checkout of the new code, run against production:
   `MONGO_URI="$(heroku config:get MONGO_URI -a <app>)" python scripts/migrations/20261016_remove_username_only_users.py`,
   then again with `--apply`. Importing `db.models` builds no indexes, so
   this is safe before deploy.
5. Before the deploy, cut off the old `patent-act-15774ac83829` app. It still
   signs in any typed username, including the random names self-signup will
   mint. Rotate the password of the Atlas database user its `MONGO_URI` uses.
   First confirm the new app's `MONGO_URI` uses a different Atlas user, or it
   is cut off too. Then check that the old app can no longer reach the
   database.
6. Run the `schema-check` preflight on production for `email`: no
   duplicates, and no document without an email.
7. Deploy, only after `LP-0002-05` has landed. `init_db()` builds `email_1`.
8. Rotate `SECRET_KEY` (`heroku config:set SECRET_KEY=…`), which ends every
   username-created session.
9. Smoke test on Heroku with two test accounts that sign themselves up.

Rollback: redeploy the previous release. It reopens username login for every
account, including self-signed-up ones, whose `learner-…` names could be
guessed, so keep any rollback short. The previous release also brings back
`scripts/add_user.py`. Deleted users and their progress come
back only from the step 3 dump.

## Implementation Order

1. Schema via `schema-check`: `UserModel.email`, the `email_1` index in
   `init_db()`, the `data-model.md` update (including the callback as a
   `users` writer), the migration script, and `tests/test_migrations.py`.
2. Add `Authlib` to `requirements.txt`, pinned to the current release. Then
   add `ProxyFix`, the Google config and startup check in `create_app()`, the
   `.env.example` vars, the `oauth` registration in `services/auth.py`, the
   `GET /auth/google` and `/auth/google/callback` routes for existing users,
   and their tests. Username login still works, so `pytest` stays green.
3. Remove `POST /auth/login` and `validate_user`, and swap `login.html` to
   the Google button and new footer. Add the 405 test.
4. Self-signup: `find_or_create_user` with the random name, the race and
   clash handling, the unverified-email copy, and their tests.
5. Delete `scripts/add_user.py` and its `add_user()` test, and remove its
   mentions from the docs and `prd-report` step 1.
6. Run the app locally against a local MongoDB with real Google credentials.
   Two test accounts sign themselves up.
