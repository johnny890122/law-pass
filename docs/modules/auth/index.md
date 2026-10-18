# Auth

Who may use the app, and how they prove it. Current truth since
[LP-0002-01](../../changelog/2026-10-16-google-sign-in.md), with LINE added by
[LP-0009](../../changelog/2026-10-18-line-login.md).

## Product rules

- **Self-signup is the only way in.** Any Google account with a verified
  email, and any LINE account, gets an account on its first sign-in. There
  is no console account creation: `scripts/add_user.py` is retired
  (2026-10-17), and admin edits, such as `is_admin`, happen in Atlas.
- **Google and LINE sign-in are the only logins**, in every environment,
  local development included. Username login is gone: `POST /auth/login`
  answers 405. There is no test bypass either. Smoke runs and `prd-report`
  sign in by hand with two dedicated test Google accounts and one LINE test
  account, which all sign themselves up (delete their `users` docs between
  runs to make them new again).
- **One account per provider identity, never linked.** A Google account is
  keyed by `users.email`, and a LINE account by `users.line_user_id`, the
  LINE ID token's `sub`. A Google sign-in reads only `email`, and a LINE
  sign-in only `line_user_id`. One person who uses both has two accounts
  with separate progress (LP-0009).
- **Who gets a LINE session.** Any LINE ID token that verifies: HS256 signed
  with the channel secret, with the right `iss`, `aud`, `exp`, and `nonce`,
  and a non-empty string `sub`. LINE sends no email, so there is no
  unverified-email refusal.
- **Who gets a session.** Any Google ID token with `email_verified: true` and
  an email. The email, stripped and lowercased, is matched against
  `users.email`, so case differences reuse the same account. A miss creates
  the account. A user whose Google email changed signs up as a new,
  unlinked account, because account linking is out of scope.
- **A new account's name.** One random name, `learner-` plus 6 hex
  characters, is both `username` and `display_name`. The learner can
  optionally change `display_name` in onboarding (LP-0002-02). `username`
  stays a fixed label, not a credential.
- **A refusal writes nothing.** Only an unverified email, a LINE token
  without a `sub`, or an OAuth failure is refused: no `users` document, no
  `last_login`, no `user_id` in the session.
- **Profile data is never stored.** Google's scope is `openid email`, and
  LINE's is `openid` alone, so LINE's name, picture, and email are never
  requested. A sign-in never overwrites `username` or `display_name`.
- **Races are settled by the unique indexes.** Two first sign-ins with the
  same email produce one account (`email_1`), and so do two with the same
  LINE `sub` (`line_user_id_1`). A random name that is taken is redrawn
  (`username_1`). Both identity indexes are unique over strings only, so the
  null `email` of every LINE account never clashes.
- **`next` is validated twice**, on the way into `/auth/google` or
  `/auth/line` and again on the way out of the callback. A foreign host
  lands on the dashboard.
- **Missing config fails startup.** `create_app()` raises, naming the missing
  variable, when `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
  `LINE_CLIENT_ID`, or `LINE_CLIENT_SECRET` is unset.
- **Behind Heroku**, `ProxyFix(x_proto=1)` trusts the router's
  `X-Forwarded-Proto`, so the OAuth `redirect_uri` is `https://`.
- **Production went live before the grading cap.** Self-signup lets anyone
  spend OpenRouter credit through short-answer grading, and LP-0002-05's
  per-user daily cap is not built yet. The user deployed it anyway on
  2026-10-17 for a production test (LP-0003).
- **No other door into the same data.** The old `patent-act-15774ac83829`
  app still has username login, but its database is not the new app's:
  `law-pass` started on an empty database on its own Atlas cluster
  (LP-0003, 2026-10-17).

## Sign-in flow

`/auth/login` reads 「請使用 Google 或 LINE 帳號登入」 and shows two
full-width buttons, each per its brand's guidelines: 「使用 Google 帳戶登入」
first, linking to `/auth/google?next=…`, then, 12px below, the green LINE
button 「使用 LINE 帳號登入」 with LINE's official icon
(`static/img/line_88.png`, unmodified from `LINE_Login_Button_Image.zip`),
linking to `/auth/line?next=…`. The footer reads 「第一次登入時會自動建立帳號」.
A signed-in visitor goes straight to the dashboard, from the login page and
from either start route.

### Google

1. The learner clicks the Google button.
2. `/auth/google` stores the validated `next` as `session['login_next']`.
   Authlib redirects to Google with `state` and `nonce`.
3. `/auth/google/callback`: Authlib checks `state`, exchanges the code, and
   verifies the ID token (signature, `iss`, `aud`, `exp`, `nonce`).
4. A verified email gets `find_or_create_user`, which finds the account or
   creates it, then `create_session(user)`, which sets `user_id`,
   `username`, and `display_name` and `$set`s `last_login`. Then 302 to
   `login_next` or the dashboard.

### LINE

1. `/auth/line` stores the validated `next` as `session['login_next']`.
   Authlib redirects to `access.line.me` with `scope=openid`, `state`, and
   `nonce`.
2. `/auth/line/callback`: Authlib checks `state`, exchanges the code at
   `api.line.me`, and verifies the ID token. LINE signs web-login ID tokens
   with HS256, keyed by the channel secret, although its discovery document
   advertises only ES256. So the `line` client is registered without
   discovery, allows HS256 only, and `create_app()` installs the channel
   secret as its only key.
3. `find_or_create_line_user` looks the `sub` up in `users.line_user_id`,
   or creates the account with `email: None` and a random name. Then
   `create_session(user)` and 302, as for Google.

| Outcome | Login page shows |
| --- | --- |
| Cancelled on Google or LINE, missing or replayed `state`, token or ID-token failure, LINE token without a `sub` | 「登入失敗，請重試」 |
| Unverified or missing email | 「此 Google 帳號的電子郵件尚未驗證，無法登入」 |
| Logged out | 「已登出」 |

## Operations

- Google Cloud Console: one Web application OAuth client. Its authorized
  redirect URIs are `http://localhost:5000/auth/google/callback`,
  `http://localhost:5001/auth/google/callback` (macOS AirPlay holds 5000),
  and `https://<app>.herokuapp.com/auth/google/callback`. Open the app at
  `localhost`, not `127.0.0.1` or a LAN address, or Google answers
  `redirect_uri_mismatch`. Publish the consent
  screen "In production". "Testing" mode adds a second allowlist on Google's
  side.
- LINE Developers Console: one LINE Login channel, app type "Web app", with
  no email permission. `LINE_CLIENT_ID` is its numeric "Channel ID", not a
  `U…` user ID, and `LINE_CLIENT_SECRET` is its "Channel secret". Its
  callback URLs are `http://localhost:5000/auth/line/callback`,
  `http://localhost:5001/auth/line/callback`, and
  `https://<app>.herokuapp.com/auth/line/callback`. Publish the channel:
  while it is "Developing", only its admins and testers can sign in.
- **Never move the LINE channel to another provider.** A LINE user ID
  belongs to the provider, so every `sub` would change, and every LINE
  learner would become a new, empty account.
- Rotating the LINE channel secret invalidates nothing stored, but it must
  reach `LINE_CLIENT_SECRET` before the next sign-in, or every LINE ID token
  fails verification.
- Rotating `SECRET_KEY` ends every session.

## Logout

The header 登出 button asks 「確定要登出嗎？」, then `GET /auth/logout` clears
the whole session, including the law choice and any sign-in in progress,
flashes 「已登出」, and lands on the login page. It writes nothing to the
database. Logging out of the app does not log out of Google, so logout
leaves one flag in the cleared session, and the next sign-in sends
`prompt=select_account`: Google shows its account chooser, and the learner
can pick any account (LP-0006). The same flag makes a LINE sign-in send
`disable_auto_login=true`, so LINE shows its login screen instead of signing
in silently (LP-0009). Whichever button the learner clicks first takes the
flag. Any other sign-in, such as a first visit, an expired app session, or a
browser restart that dropped the flag, leaves it to the provider, which may
sign in silently.

Known limits, accepted because session hardening is out of scope
(LP-0002-01):

- Logout answers GET, so another site can sign a learner out with a link or
  an image.
- The session is a signed cookie, so a cookie copied before logout keeps
  working until it expires (7 days) or `SECRET_KEY` rotates.

## Manual checks

Automation cannot sign in to real Google, and there is no bypass. Smoke runs
and `prd-report` walk these by hand in the Playwright browser, at
`http://localhost:<port>`, with two test Google accounts (LP-0005):

1. Retired on 2026-10-17, with console account creation. The number is kept
   so the tickets' check numbers stay valid.
2. A new account signs itself up and shows `learner-…` in the header. Sign
   out and in again, and the database still holds one account for it.
3. Cancel on Google's screen → 「登入失敗，請重試」.
4. Opening the app at `127.0.0.1` gets Google's `redirect_uri_mismatch`.
5. Header 登出 → 「確定要登出嗎？」. Cancel keeps you signed in. OK lands on
   the login page with 「已登出」.
6. After logout, browser Back, then reload or click anything → the login
   page, and no account data loads.
7. Logout in one tab → the other tab's next page load or action goes to the
   login page.
8. After logout, sign in again → Google's account chooser appears (LP-0006).
9. Logout, then sign in with the other test account → the header shows the
   second account's name.
10. Production, after LP-0003 and LP-0002-05: the `https://` callback on the
    Heroku app, with two accounts that sign themselves up (`LP-0007`, the
    production cutover).
11. The LINE test account signs itself up and shows `learner-…` in the
    header. Sign out and in again, and the database still holds one
    account for it (LP-0009).
12. After logout, the LINE button shows LINE's login screen rather than
    signing in silently (LP-0009).
13. Production: the LINE test account signs itself up through the
    `https://` callback on the Heroku app (LP-0009).

The account-switch check (9) stays Google-only. An unverified email cannot
be produced with a real Google account, and a token without a `sub` cannot
be produced with a real LINE account, so those refusals are covered by tests
only.

## Code

- `routes/auth.py`: `/auth/login`, `/auth/google`, `/auth/google/callback`,
  `/auth/line`, `/auth/line/callback`, `/auth/logout`, `/auth/current`,
  `next` validation, and the `choose_account` flag.
- `services/auth.py`: the `oauth` Google and LINE clients,
  `find_or_create_user`, `find_or_create_line_user`, the shared
  `_find_or_create`, `new_username`, `create_session`, and `login_required`.
- `app.py`: the `OAUTH_CONFIG` check, `oauth.init_app`, the LINE HS256 key,
  and `ProxyFix`.
- `templates/login.html` and `static/img/line_88.png`: the Google and LINE
  buttons.
- `tests/test_auth.py`: both flows, logout, and real ID-token verification
  with locally signed tokens (RS256 for Google, HS256 for LINE). Neither
  provider is ever called.
