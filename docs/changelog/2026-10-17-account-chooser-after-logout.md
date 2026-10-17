# 2026-10-17 — Account chooser after logout

**LP ids:** LP-0006

After logout, signing in again put the same Google account straight back in,
so a learner could not switch accounts without signing out of Google. LP-0005
manual check 8 found it. Now the first sign-in after a logout shows Google's
account chooser. Rules live in
[`docs/modules/auth/index.md`](../modules/auth/index.md).

| Area | Was | Now |
| --- | --- | --- |
| Sign-in after logout | Google answered `prompt=none` and returned the same account with no screen. | `prompt=select_account`: Google's account chooser, so any account can be picked. Once per logout. |
| Other sign-ins | Google's default. | Unchanged: Google's default, which may sign in silently. |
| Logout | Cleared the session. | Clears the session, then leaves a one-time `choose_account` flag. |

## Deliberately not done

- Logging the learner out of Google itself (federated logout).
- A 「使用其他帳號登入」 link on the login page.
- Forcing the chooser on every sign-in.
- Keeping the flag across a browser restart. The session cookie is not
  permanent, so a sign-in after a restart is left to Google.
