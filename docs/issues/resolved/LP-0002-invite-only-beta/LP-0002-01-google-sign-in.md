---
id: LP-0002-01
title: Google sign-in with self-signup
type: story
status: resolved
priority: high
created: 2026-10-16
resolved: 2026-10-18
area: auth
parent: LP-0002
tags:
  - sso
  - security
  - signup
---

# Google sign-in with self-signup

## Description

Login today trusts any typed username, with no password, on a public Heroku
URL. Learners need to sign in with Google, and anyone with a verified Google
account may sign themselves up on their first sign-in.

## Details

- Current: `POST /auth/login` takes a `username` and signs in whenever it
  exists (`services/auth.py` `validate_user`). Accounts come from
  `scripts/add_user.py <username> <display_name>`. `users` has no email.
- Desired:
  - `login.html` shows a single Google sign-in button. It uses Google OIDC
    (authorization code flow with `state`). On callback, the Google-verified
    email (`email_verified` true) is looked up in `users.email`.
  - A match runs `create_session(user)` as it does today.
  - No match is a self-signup. The callback inserts a `users` doc with the
    lowercased email, one system-generated random name used as both
    `username` and `display_name` (unique against `username_1`), and
    `created_at`, then runs `create_session`. A second sign-in finds that doc
    and creates no other. The random-name format is the PRD's.
  - An unverified email gets no session and creates no `users` doc. The login
    page says why.
  - There is no console account creation. `scripts/add_user.py` and its test
    are deleted, so every account comes from self-signup. `users.email` gets
    a unique index. Admin edits, such as `is_admin` in `LP-0002-03`, happen
    in Atlas.
  - Existing username-only users are removed at cutover, because they will
    no longer use the app. No emails are backfilled. Every account after
    cutover is keyed by email.
  - Username login is retired everywhere, including local development: the
    `POST /auth/login` username form and its route are removed. The
    `users.username` field stays as a stored label.
  - `users.display_name` starts as the random name, which the learner can optionally change in `LP-0002-02`'s
    onboarding. `username` stays a fixed label. Google profile data
    is never requested or stored, so the scope stays `openid email`, and a
    sign-in never overwrites `display_name`.
  - The login footer 「如果您沒有帳號，請聯繫管理員」 no longer holds, because
    signing in creates the account. The PRD proposes new copy.
  - New env vars: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`, in
    `.env.example` and in the Heroku config.
- Verify Google's ID token with a maintained library such as Authlib or
  google-auth. Never hand-roll JWT verification. This adds one dependency.
- Schema change: `users.email`, the unique `email_1` index, the callback as a
  new `users` writer, and the migration that deletes username-only users go
  through `schema-check`. The PRD's Data Changes table is its input.
- Verification after cutover: smoke runs and `prd-report` walks sign in by
  hand with two dedicated test Google accounts, both signing themselves up.
  Delete their `users` docs from the local DB between runs to make them new
  again (epic Settled Decisions). `.claude/skills/prd-report/SKILL.md` step 1
  still provisions with `add_user.py <name> "<display>"` and assumes a typed
  login, so this ticket updates it to self-signup only.
- Deploys through `LP-0003`. The new law-pass Heroku app that ticket creates
  is the `<app>` in the PRD's Rollout, and `LP-0003` lands first.
- Production self-signup opens only after `LP-0002-05` (per-user daily cap on
  LLM grading) lands. This ticket's code is built and checked locally before
  then.
- The production cutover (the PRD's Rollout) is its own ticket, `LP-0007`.
  This ticket resolves on local verification and its approved report.
- PRD: `docs/prd/LP-0002-01-google-sign-in.md`. It was approved for
  invite-only on 2026-10-16 and for self-signup on 2026-10-17, then revised
  again on 2026-10-17 to drop console account creation. It must be approved
  again before this ticket returns to `in_progress`.
- No artifact — the form is swapped for a single Google button that follows
  Google's branding guidelines, so there is no layout choice to make.
- Out of scope: other providers (LINE, Apple), account linking, signup by any
  route other than Google sign-in, and session hardening beyond what the
  OAuth flow needs.

## Acceptance Criteria

- [x] A provisioned Google account signs in and reaches the dashboard. No
      longer applies: console account creation was removed on 2026-10-17,
      and every account signs itself up (next box).
- [x] A verified Google account with no `users` doc signs itself up. One doc
      is created with its lowercased email and one random name as both
      `username` and `display_name`, and it gets a session. Signing in again creates no second doc.
- [x] No username-only user remains in `users` after cutover. Moved to
      `LP-0007`, which runs the production cutover.
- [x] An unverified Google account is refused, and no `users` doc is created.
      Covered by tests only (`tests/test_auth.py`): a real Google account
      cannot be unverified.
- [x] Posting a bare username to `/auth/login` no longer creates a session,
      in any environment.
- [x] A Google login leaves `users.display_name` unchanged.
- [x] `scripts/add_user.py` and its test are deleted, and `users.email` is
      unique.
- [x] `schema-check` passed. `data-model.md` lists `users.email`, `email_1`,
      and the callback as the only `users` insert writer. Its Change Log row's
      production `Ran` cell is filled by `LP-0007`.
- [x] `pytest` green — covered by `tests/test_auth.py` and
      `tests/test_migrations.py`, with the Google token exchange mocked.
- [x] `flake8` clean.
- [x] Seen working in the running app: two test Google accounts sign
      themselves up, against a local MongoDB.
- [x] Docs synced: `docs/modules/auth/index.md` (new),
      `docs/modules/index.md`, `docs/modules/db/data-model.md` (through
      `schema-check`), and `.claude/skills/prd-report/SKILL.md` step 1, plus a
      changelog entry.
- [x] Report at `docs/reports/LP-0002-01-google-sign-in/report.md` is
      approved.

## Open Questions

- None.

## Live Results (2026-10-17)

- Self-signup: `j087061439@gmail.com` and `johnny.chang@moblab.com` each
  signed themselves up on first sign-in with `learner-…` names, and later
  sign-ins reused the same accounts (local `patent_act` and `law_pass`
  databases).
- A console-created account no longer applies (2026-10-17).

## Resolution

Google sign-in replaced username login, and a first sign-in with a verified
email creates the account under a random `learner-…` name. Console account
creation is gone. The production cutover, including deleting username-only
users, was deliberately left to `LP-0007`. See the
[changelog](../../../changelog/2026-10-16-google-sign-in.md) and the
[report](../../../reports/LP-0002-01-google-sign-in/report.md).

## Related Files

- `app.py`
- `routes/auth.py`
- `services/auth.py`
- `templates/login.html`
- `scripts/add_user.py` (deleted)
- `scripts/migrations/` (new)
- `db/models.py`
- `.env.example`
- `requirements.txt`
- `tests/test_auth.py`
- `tests/test_migrations.py` (new)
- `tests/test_app.py`
- `docs/prd/LP-0002-01-google-sign-in.md`
- `docs/modules/db/data-model.md`
- `.claude/skills/prd-report/SKILL.md`

## Handoff Appendix

### Settled Decisions

- Self-signup is allowed: any Google account with a verified email gets an
  account on its first sign-in. This reverses the invite-only decision.
  Decided by the user on 2026-10-16.
- A self-signed-up account starts with one system-generated random name as
  both `username` and `display_name`. The learner can optionally change
  `display_name` in `LP-0002-02`'s onboarding, and `username` stays a fixed
  label. Decided by the user on 2026-10-17, replacing the email-derived
  names decided on 2026-10-16 and earlier on 2026-10-17.
- No console account creation. `scripts/add_user.py` is deleted entirely,
  every account comes from self-signup, and admin edits happen in Atlas.
  Decided by the user on 2026-10-17.
- The production cutover is split into its own ticket, `LP-0007`. Decided by
  the user on 2026-10-17.
- Short-answer grading spend is bounded by a per-user daily cap in
  `LP-0002-05`, and production self-signup waits for it. Decided by the user
  on 2026-10-17.
- Username login has no fallback anywhere: not for local development, and not
  for a transition window. Decided by the user on 2026-10-16.
- Existing username-only users are removed rather than backfilled, because
  they will no longer use the app. This replaces the earlier
  "backfill every email" decision. Their documents in `user_progress`,
  `user_law_stars`, `user_law_stats`, `user_question_stars`,
  `user_daily_stats`, and `sessions` are deleted with them, leaving no
  orphans. Decided by the user on 2026-10-16, during the PRD gap analysis.
- `SECRET_KEY` is rotated on Heroku at cutover, so sessions created by
  username login end at once. Decided by the user on 2026-10-16.
- `users.username` stays as a stored label, not a login credential. Decided
  by the user on 2026-10-16.
- Google profile data is never stored, and a sign-in never overwrites
  `display_name`, whether the signup or the learner set it. Decided by the
  user on 2026-10-16, and kept when self-signup was allowed.
- The old `patent-act-15774ac83829` app is cut off before cutover by rotating
  the Atlas database user its `MONGO_URI` uses, so it can no longer reach the
  shared database. The new `LP-0003` app must use its own Atlas user first.
  Decided by the user on 2026-10-16.

### Behavior Details

- Two first sign-ins racing on the same new email: the unique `email_1` index
  lets one insert win, and the other must then find that doc rather than
  fail.
- The random name uses only letters, digits, and `-`. A clash on `username_1` retries with a new random name.

### Test Scenarios

- `tests/test_auth.py`, with Google's token endpoint and ID-token verification
  mocked:
  - Existing account, verified email → 302 to the dashboard,
    `session['user_id']` equals its `_id`, `last_login` is set,
    and `display_name` is unchanged even when Google's profile name differs.
  - New verified email → 302 to the dashboard, one `users` doc with the
    lowercased email, one random name as both `username` and
    `display_name`, and `session['user_id']` is
    its `_id`. A second sign-in → the same `_id`, still one doc.
  - A random name that clashes with an existing `username` → a new random
    name is drawn (stub the generator).
  - `email_verified: false` → refused, and the `users` count is unchanged.
  - `state` mismatch on the callback → refused.
  - `POST /auth/login` with `username=alice` → no session.
