---
id: LP-0005
title: Full test coverage for Google sign-in
type: improvement
status: in_progress
priority: medium
created: 2026-10-17
resolved:
area: tests
tags:
  - sso
  - security
  - auth
---

# Full test coverage for Google sign-in

## Description

`LP-0002-01`'s tests stub Google's whole token exchange, so Authlib's real
ID-token checks never run in our suite, and several session and routing edges
are untested. This ticket covers the full Google sign-in test list: automated
cases, plus a manual live-Google checklist for what automation cannot reach.

## Details

- Current: `tests/test_auth.py` stubs `oauth.google.authorize_access_token`
  whole and covers sign-in, self-signup, the name clash, the same-email race,
  unverified emails, forged `state`, `?error=`, the 405, `next`, and the
  `https` `redirect_uri`. `tests/test_migrations.py` and `tests/test_app.py`
  cover the migration and the login page. Nothing exercises signature, `iss`,
  `aud`, `exp`, or `nonce` verification, the startup config check, the
  logout flow, `/auth/current`, or the cookie flags.
- Logout today: the header 登出 button (`templates/base.html:51`) runs
  `logout()` (`static/js/main.js:33`), which asks 「確定要登出嗎？」 and, on OK,
  navigates to `GET /auth/logout`. The route (`routes/auth.py:68`, GET or
  POST) calls `session.clear()`, flashes 「已登出」, and redirects to
  `/auth/login`.
- Desired: every case below passes. The ✅ cases exist today and stay; the
  rest are added. Case numbers match the list agreed on 2026-10-17.
  - **A. Sign-in outcomes** (claims stubbed), `tests/test_auth.py`:
    - ✅ A1 Existing account → dashboard, `session.user_id`, `last_login`
      set, `display_name` unchanged by a differing `name` claim, email case
      ignored.
    - ✅ A2 New verified email → one `learner-xxxxxx` account, reused on the
      second sign-in.
    - ✅ A3 Random-name clash → a new name is drawn.
    - ✅ A4 Same-email race → one account.
    - ✅ A5 `email_verified` false or missing, or no email → refused, nothing
      written.
    - A6 Token with no `userinfo` → refused, nothing written.
    - A7 `email_verified: "true"` as a string → refused. Only boolean `true`
      counts.
    - A8 Five name clashes in a row → 500, and nothing written. This is the
      known ceiling, not a target to fix.
  - **B. OAuth protocol and real ID-token verification**,
    `tests/test_auth.py`, which already has the fixtures these tests need.
    Only the HTTP token exchange is
    stubbed. The ID token is signed with a local test key whose public JWK
    sits inline in the stubbed discovery metadata:
    - B9 Valid signed ID token → signs in.
    - B10 Wrong `aud` → 「登入失敗，請重試」, nothing written.
    - B11 Wrong `iss` → refused.
    - B12 `exp` past Authlib's 120-second leeway → refused.
    - B13 Signed by a different key → refused.
    - B14 `nonce` mismatch → refused.
    - ✅ B15 Unknown or forged `state` → refused.
    - ✅ B16 `?error=access_denied` → refused.
    - B17 Callback replayed after a successful sign-in → refused, and the
      session is unchanged.
    - B18 Token endpoint failure (`invalid_grant`) → refused.
    - B19 Two tabs start sign-in → each callback succeeds once.
  - **C. Session and routing**, `tests/test_auth.py`:
    - ✅ C20 `POST /auth/login` → 405.
    - ✅ C21 `next` with a foreign host → dashboard; a same-host path is kept.
    - C22 Signed-out visit to a protected page → login page, the button
      carries `next`, and after sign-in the learner lands on that page.
    - C23 Already signed in → `/auth/login` and `/auth/google` go to the
      dashboard, with no trip to Google.
    - C24 `login_next` is used once, not again by a later callback.
    - C25 Logout: see group F.
    - C26 `/auth/current` → 401 signed out; `user_id`, `username`, and
      `display_name` signed in.
    - ✅ C27 Behind `X-Forwarded-Proto: https`, `redirect_uri` is `https://`;
      `scope=openid email`; `state` and `nonce` present.
    - C28 Session cookie is `HttpOnly` and `SameSite=Lax`, plus `Secure`
      when `FLASK_ENV=production`.
  - **D. Config, accounts, data**:
    - D29 Missing `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET` →
      `create_app()` raises, naming the missing variable
      (`tests/test_auth.py`).
    - D30 Removed with `scripts/add_user.py` on 2026-10-17.
    - ✅ D31 Migration: dry run, apply, idempotent second apply
      (`tests/test_migrations.py`).
    - D32 `init_db()` raises when `users` holds documents without an email,
      because `email_1` cannot be built (`tests/test_app.py`, next to the
      other unique-index cases).
  - **E. Manual, live Google**: signed in by hand in the Playwright browser,
    because the epic allows no login bypass. Written into
    `docs/modules/auth/index.md` as a checklist that smoke runs and
    `prd-report` walk:
    - E33 No longer applies: console account creation was removed on
      2026-10-17.
    - E34 A new account signs itself up (`learner-…` in the header). Sign
      out and in again, and the database still holds one account for it.
    - E35 Cancel on Google's screen → 「登入失敗，請重試」.
    - E36 Opening the app at `127.0.0.1` gets Google's
      `redirect_uri_mismatch`, so the "use `localhost`" rule holds.
    - E37 Production: the `https://` callback on the Heroku app, with one
      two self-signed-up accounts. This runs as
      `LP-0007`, the production cutover, after `LP-0003` and `LP-0002-05` land.
      This ticket only writes it into the checklist and does not wait for it.
  - **F. Logout.** Automated in `tests/test_auth.py`:
    - F38 Signed in, `GET /auth/logout` → 302 `/auth/login` showing 「已登出」,
      and the session holds no `user_id`, `username`, or `display_name`.
    - F39 `POST /auth/logout` behaves the same.
    - F40 Logout clears every session key, including `current_law_type`,
      `login_next`, and Authlib's state. A sign-in started before logout
      cannot complete: its callback → 「登入失敗，請重試」.
    - F41 After logout, a protected page → `/auth/login?next=…`,
      `/auth/current` → 401, and a `login_required` API call is refused.
    - F42 Logout while already signed out → the same 302 and 「已登出」, with
      no error.
    - F43 Logout writes nothing: the `users` doc, `last_login` included, is
      unchanged, and no per-user data is touched.
    - F44 Sign in again after logout → the same `_id`, with no second
      self-signup, and a `learner-…` name is kept.
    - F45 Logout, then sign in as a different Google account → the session
      is the second user's, with nothing left from the first.

    Manual, live Google, added to the E checklist:
    - F46 Header 登出 → 「確定要登出嗎？」. Cancel keeps you signed in; OK lands
      on the login page with 「已登出」.
    - F47 After logout, browser Back, then reload or click anything → the
      login page, and no account data loads.
    - F48 Logout in one tab → the other tab's next page load or action goes
      to the login page.
    - F49 After logout, 「使用 Google 帳戶登入」 again. Logging out of the app
      does not log out of Google, so record whether Google shows the account
      chooser or signs the same account straight back in. If the learner
      cannot pick another account, file a bug (likely fixed with
      `prompt=select_account`).
    - F50 Switch accounts: logout, then sign in with the other test account →
      the header shows the second account's name.
  - An unverified email cannot be produced with a real Google account, so
    A5 stays tests-only.
  - Known limits, documented here and not tested as targets, because session
    hardening is out of scope in `LP-0002-01`:
    - Logout answers GET, so another site can sign a learner out with a
      link or image.
    - Flask's session is a signed cookie, so a cookie copied before logout
      keeps working until it expires (7 days) or `SECRET_KEY` rotates.
- Depends on `LP-0002-01`'s code, which these tests target. It is a
  follow-up: `LP-0002-01` resolves on its own tests and does not wait for
  this ticket.
- No PRD — tests and a checklist only, and Details lists every case.
- No artifact — no screen changes.
- Out of scope: changing sign-in or logout behavior (a failing case that
  reveals a defect gets its own bug ticket), the known limits above, load or
  rate testing, and automating real Google sign-in.

## Acceptance Criteria

- [x] Every A–D case and F38–F45 has a passing test. The ✅ cases keep
      passing.
- [x] Group B runs Authlib's real ID-token verification with locally signed
      tokens, with no network call and no new dependency.
- [x] `pytest` green — covered by `tests/test_auth.py`, `tests/test_app.py`,
      and `tests/test_migrations.py`. Google and OpenRouter are never called.
- [x] `flake8` clean.
- [ ] Seen working in the running app: E34–E36 and F46–F50 walked by hand
      against a local MongoDB, with screenshots at phone size. F49's result
      (chooser shown or not) is recorded, with a bug ticket filed if the
      learner cannot switch accounts.
- [x] Docs synced: `docs/modules/auth/index.md` gains the manual checklist
      (E and F46–F50) and the two known logout limits. No changelog entry,
      because no behavior changes.

## Open Questions

- None.

## Related Files

- `tests/test_auth.py`
- `tests/test_app.py`
- `tests/test_migrations.py`
- `services/auth.py`
- `routes/auth.py`
- `app.py`
- `templates/base.html`
- `static/js/main.js`
- `docs/modules/auth/index.md`
- `docs/prd/LP-0002-01-google-sign-in.md`

## Handoff Appendix

### Settled Decisions

Decided by the user on 2026-10-17:

- A standalone follow-up ticket, outside the `LP-0002` epic.
  `LP-0002-01` does not wait for it.
- Both automated cases (A–D) and a manual live-Google checklist (E).
- Group B signs real ID tokens with a local test key and runs Authlib's real
  verification.
- Check 1 (E33) and D30 are dropped with console account creation, and check
  3 (E35) is walked live. Decided by the user on 2026-10-17.

### Live Results (2026-10-17)

- Manual check 2 (E34): `j087061439@gmail.com` signed itself up as
  `learner-a00a07`, and a later sign-in reused that account.
- Manual check 4 (E36): `127.0.0.1:5001` gets Google's
  `redirect_uri_mismatch`.
- Manual checks 5–7 (F46–F48): Cancel at 「確定要登出嗎？」 sent no request.
  OK landed on the login page with 「已登出」. Back re-requested `/` from the
  server and was redirected to sign-in. A stale tab's next click went to
  `/auth/login?next=…`.
- Manual check 8 (F49): **no chooser.** Google answered `prompt=none` and
  signed the same account straight back in, so the learner cannot switch
  accounts. Filed as `LP-0006`, resolved the same day. After the fix, a
  logout led to Google's account chooser (12:16:13).
- Manual check 9 (F50): passed after `LP-0006`. 「使用其他帳戶」 signed in as
  a second account, which signed itself up (12:17:18, local `law_pass`
  database).
- Check 1 (E33) no longer applies: console account creation was removed.
- Check 3 (E35) is walked during `LP-0002-01`'s report run, after the user
  revokes law-pass access for one account so the consent screen appears.

### Behavior Details

- Group B: Authlib's `fetch_jwk_set` returns `metadata['jwks']` when it is
  present, so the stubbed discovery dict carries the test key's public JWK
  inline, and no JWKS fetch happens. Stub only
  `oauth.google.fetch_access_token` to return
  `{'access_token': …, 'id_token': <signed JWT>}`.
- The `nonce` lives in Authlib's state data. A B test starts at
  `GET /auth/google`, reads `state` and `nonce` from the Google redirect URL,
  signs that `nonce` into the token (or a wrong one for B14), and calls the
  callback with that `state`.
- `cryptography` and `joserfc` are already installed by `Authlib`, so signing
  needs no new dependency.
- D32: `users` already has `username_1`, so the two email-less documents need
  distinct usernames to reach the `email_1` failure.
