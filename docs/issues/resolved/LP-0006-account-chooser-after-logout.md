---
id: LP-0006
title: Show Google's account chooser on the first sign-in after logout
type: bug
status: resolved
priority: medium
created: 2026-10-17
resolved: 2026-10-17
area: auth
tags:
  - sso
  - logout
---

# Show Google's account chooser on the first sign-in after logout

## Description

After a learner logs out, the next 「使用 Google 帳戶登入」 signs the same Google
account straight back in, so they cannot switch accounts without signing out
of Google itself. Found by `LP-0005` manual check 8 (F49) on 2026-10-17.

## Details

- Current: `GET /auth/google` (`routes/auth.py:40`) calls
  `authorize_redirect(redirect_uri)` with no `prompt`. Logout
  (`routes/auth.py:68-72`) clears only the app session, and Google keeps its
  own. With consent already given, Google answers `prompt=none` and returns
  the same account with no screen at all. Seen live on 2026-10-17 at
  12:12:37: `/auth/google`, the callback, and the dashboard all within one
  second.
- Desired:
  - After an intentional logout, the next sign-in shows Google's account
    chooser (`prompt=select_account`), so the learner can pick any account.
  - Otherwise, sign-in keeps Google's default, which may sign in silently.
    This covers a first visit and an app session that expired.
  - Shape: logout leaves a one-time flag in the cleared session, and
    `/auth/google` sends `prompt=select_account` when the flag is present,
    then drops it.
- The flag lives in the session cookie, which the browser drops when it
  closes, because sessions are not marked permanent. A sign-in after a
  browser restart therefore falls under "otherwise", which is expected.
- This adds `prompt` to the `GET /auth/google` contract in `LP-0002-01`'s
  approved PRD, for this one case. The user decided it on 2026-10-17. The
  auth module doc records it as current truth.
- No PRD — one session flag and one redirect parameter.
- No artifact — Google's chooser is Google's screen, and the app's screens do
  not change.
- Out of scope: logging the learner out of Google (federated logout), a
  「使用其他帳號登入」 link, and forcing the chooser on every sign-in.

## Acceptance Criteria

- [x] After logout, `/auth/google` redirects to Google with
      `prompt=select_account`, once.
- [x] Without a preceding logout (a fresh session, or a later sign-in), the
      redirect carries no `prompt`.
- [x] `pytest` green — covered by `tests/test_auth.py`. `LP-0005`'s F40 test
      is updated to allow the logout flag.
- [x] `flake8` clean.
- [x] Seen working in the running app: log out, sign in, and Google's account
      chooser appears. Picking the other test account signs in as it. This
      also completes `LP-0005` manual check 9 (switch accounts). Note: check 3
      (cancel on Google's screen) was not reached, because the chooser has no
      cancel and the consent screen was accepted. It stays on `LP-0005`.
- [x] Docs synced: `docs/modules/auth/index.md` (the Logout section and
      manual check 8), plus a changelog entry.

## Open Questions

- None.

## Resolution

Logout now leaves a one-time flag, so the next sign-in sends
`prompt=select_account` and Google shows its account chooser. Other sign-ins
stay one click. Seen live on 2026-10-17: a logout led to the chooser, and
「使用其他帳戶」 signed in as a second account. Lands with `LP-0002-01`'s
code, uncommitted at resolution. See
[2026-10-17-account-chooser-after-logout](../../changelog/2026-10-17-account-chooser-after-logout.md).

## Related Files

- `routes/auth.py`
- `tests/test_auth.py`
- `docs/modules/auth/index.md`
- `docs/issues/in_progress/LP-0005-google-sso-test-coverage.md`

## Handoff Appendix

### Settled Decisions

- After an intentional logout, the next sign-in shows the account chooser.
  Otherwise sign-in depends on whether the Google sign-in has expired.
  Decided by the user on 2026-10-17.

### Test Scenarios

- `tests/test_auth.py`:
  - Sign in, log out, then `GET /auth/google` → the Google URL carries
    `prompt=select_account`. A second `GET /auth/google` → no `prompt`.
  - A fresh session → `GET /auth/google` carries no `prompt`.
