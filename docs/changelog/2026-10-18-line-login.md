# 2026-10-18 — LINE Login with self-signup

**LP ids:** LP-0009

Most learners in Taiwan live in LINE, so they can now sign up and sign in
with their LINE account, through the same self-signup flow Google uses.
Rules live in [`docs/modules/auth/index.md`](../modules/auth/index.md), the
schema in [`docs/modules/db/data-model.md`](../modules/db/data-model.md),
and the spec is [`docs/prd/LP-0009-line-login.md`](../prd/LP-0009-line-login.md).

| Area | Was | Now |
| --- | --- | --- |
| Login page | Subtitle 「請使用 Google 帳號登入」 and one Google button. | Subtitle 「請使用 Google 或 LINE 帳號登入」. The Google button, then, 12px below, a green LINE button 「使用 LINE 帳號登入」 with LINE's official icon, per LINE's login button guidelines. |
| LINE sign-in | — | `GET /auth/line` and `GET /auth/line/callback`. Authlib with `state` and `nonce`, scope `openid` alone. The ID token is verified as HS256 with the channel secret, with discovery off, since LINE advertises only ES256. |
| New accounts | A first Google sign-in only. | A first LINE sign-in also creates one: `line_user_id` = the token's `sub`, `email: None`, and one `learner-` random name. |
| Linking | — | None. One person with Google and LINE has two accounts. |
| Refusal | 「登入失敗，請重試」 for OAuth failures. | The same message for a LINE cancel, bad `state`, token or ID-token failure, or a missing `sub`. Nothing is written. |
| Logout | The next Google sign-in sends `prompt=select_account`. | The flag goes to whichever button is clicked first. LINE sends `disable_auto_login=true`. |
| `users` schema | `email` required, with unique `email_1`. | `email` optional (null on LINE accounts). New `line_user_id`. `email_1` and `line_user_id_1` are unique over strings only. `init_db()` rebuilds the old `email_1` once at boot. |
| LP-0002-01 cleanup | Deleted users without an `email` field. | Deletes only users with neither a string `email` nor a string `line_user_id`, so LINE accounts are kept. |
| Config | `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` required. | `LINE_CLIENT_ID` and `LINE_CLIENT_SECRET` are required too, and startup fails without them. |
| Google sign-in | — | Unchanged. Its find-or-insert loop moved into the shared `_find_or_create`, and a new Google account also stores `line_user_id: None`. |

Deploy note: set `LINE_CLIENT_ID` and `LINE_CLIENT_SECRET` on `law-pass`
before the merge to `main`, or the new release crash-loops. At boot,
`init_db()` drops the unfiltered `email_1` and builds the partial `email_1`
and `line_user_id_1`. A Heroku rollback is clean only until the second LINE
signup: after that, two null emails block the old index, so fix forward.

Deployed as release v13 (`db9dbbc`) on 2026-10-18. Its first boot crashed
once: both gunicorn workers ran the one-time `drop_index('email_1')`, and the
second found the index already gone. Heroku restarted the dyno about 12
seconds later, the drop was skipped, and the app has been up since. Any
database that still holds the unfiltered `email_1` will do the same once
under more than one worker.

## Deliberately not done

- Account linking or merging Google and LINE accounts.
- LINE's email scope, and applying for LINE's email permission.
- Storing the LINE profile name or picture.
- LIFF, and auto-login inside LINE's in-app browser.
- The `bot_prompt` LINE Official Account friend prompt, and LINE messaging.
- Apple sign-in.
- Checking at startup that `LINE_CLIENT_ID` is numeric. A `U…` user ID put
  there by mistake boots fine, and LINE answers 400 on the first sign-in.
