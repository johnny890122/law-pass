# 2026-10-16 — Google sign-in with self-signup

**LP ids:** LP-0002-01

Login no longer trusts a typed username on a public URL. Learners sign in
with Google, and a first sign-in creates the account. Invite-only was the
first plan and was reversed before landing (2026-10-17). Rules live in
[`docs/modules/auth/index.md`](../modules/auth/index.md), and the spec is
[`docs/prd/LP-0002-01-google-sign-in.md`](../prd/LP-0002-01-google-sign-in.md).

| Area | Was | Now |
| --- | --- | --- |
| Login | `POST /auth/login` with a `username`, and no password. | One 「使用 Google 帳戶登入」 button, footer 「第一次登入時會自動建立帳號」. Google OIDC (Authlib) with `state` and `nonce`. `POST /auth/login` → 405, everywhere. |
| New accounts | Admin-only, from the console. | Self-signup: a verified Google email with no account gets one on first sign-in, named `learner-` plus 6 hex characters (both `username` and `display_name`). |
| Refusal | 「用戶名稱不存在，請聯繫管理員」 | Only an unverified email: 「此 Google 帳號的電子郵件尚未驗證，無法登入」. A cancel or OAuth failure: 「登入失敗，請重試」. Nothing is written. |
| Console accounts | `add_user.py <username> <display_name>` | `add_user.py <email> <username> <display_name>`, now optional. The email is stored lowercased and must be unique. `--list` shows it. |
| `users` schema | `username` was the login key. | `email` (required, unique `email_1`) is the login key. `username` is a stored label. The sign-in callback is a new writer. |
| Username-only users | — | Deleted at cutover with their documents in the six per-user collections, by `scripts/migrations/20261016_remove_username_only_users.py`. |
| Old `patent-act-15774ac83829` app | Shares the production Atlas database, with username login. | Cut off at cutover by rotating the Atlas user in its `MONGO_URI`. |
| Config | `SECRET_KEY` only. | `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are required, and startup fails without them. `ProxyFix` makes the `redirect_uri` https behind Heroku. |
| Dependencies | — | `Authlib==1.9.1`, which brings `joserfc` and `cryptography`. |
| `prd-report` | Step 1 made a typed-login account. | Step 1 uses two test Google accounts, one created from the console and one that signs itself up, signing in by hand. |

Deploy note: order matters. It ships through `LP-0003`'s new app, and only
after `LP-0002-05` caps LLM grading per user per day, since self-signup lets
anyone spend OpenRouter credit. `init_db()` builds the unique `email_1` at
boot, so a `users` document without an email crash-loops the dyno. Before
deploying: dump, run the migration with `--apply`, cut off the old app, and
run the `email` preflight. Then deploy and rotate `SECRET_KEY` (PRD Rollout,
steps 3–9). The `data-model.md` Change Log row reads `pending: heroku` until
then.

## Deliberately not done

- Other providers (LINE, Apple), and account linking. A changed Google email
  signs up as a new account.
- Session hardening beyond what the OAuth flow needs, such as regenerating
  the session on sign-in.
- A test-only login bypass. Smoke runs sign in by hand with two test Google
  accounts.
- Backfilling emails for username-only users. They are deleted instead.
- Removing `users.username` or its `username_1` index.
- A code switch for self-signup. Production gating is deploy order only.
- Letting learners pick their own name at signup. They start with a random
  name, and LP-0002-02's onboarding lets them change `display_name`.
