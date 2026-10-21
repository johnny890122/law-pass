---
id: LP-0009
title: LINE Login with self-signup
type: feature
status: resolved
priority: medium
created: 2026-10-17
resolved: 2026-10-18
area: auth
tags:
  - sso
  - line
  - signup
---

# LINE Login with self-signup

## Description

Google is the only way in today, but most learners in Taiwan live in LINE.
They need to sign up and sign in with their LINE account, through the same
self-signup flow Google uses.

## Details

- Current: Google sign-in is the only login (`docs/modules/auth/index.md`),
  and every account is keyed by Google-verified `users.email`, which is
  required and unique (`email_1`). `LP-0002-01` put LINE out of scope.
- Desired:
  - `login.html` keeps the Google button on top and adds a LINE button below
    it, per LINE's login button guidelines.
  - `/auth/line` and `/auth/line/callback` mirror `/auth/google`. An Authlib
    client `line` uses `state` and `nonce`, the same `login_next` /
    `_safe_next` handling, and the same `create_session(user)`.
  - The callback keys the account by the ID token's `sub` (the LINE user ID),
    looked up in a new `users.line_user_id`. A match signs in. A miss is a
    self-signup: one `users` doc with `line_user_id`, one `learner-` random
    name as both `username` and `display_name` (`new_username()`), and
    `created_at`, with no email.
  - No account linking. One person who uses both Google and LINE has two
    separate accounts, and neither sign-in touches the other's doc.
  - LINE profile data and email are never requested or stored. The scope is
    `openid` alone, which LINE accepts. A sign-in never overwrites
    `display_name`.
  - Refusals write nothing: a cancel on LINE, a missing or replayed `state`,
    a token or ID-token failure, or a missing `sub` → 「登入失敗，請重試」.
  - After logout, the next LINE sign-in sends `disable_auto_login=true`, the
    LINE counterpart of Google's `prompt=select_account` (`LP-0006`). The
    one-time `choose_account` flag goes to whichever button the learner
    clicks first.
  - New env vars: `LINE_CLIENT_ID` and `LINE_CLIENT_SECRET` (LINE's
    "Channel ID" and "Channel secret"). Authlib reads these names directly.
    They go in `.env.example`, the tests' env defaults, and the Heroku
    config. Missing either one fails startup, the same as Google's config.
- Verify LINE's ID token with Authlib, never by hand-rolled JWT code. LINE
  signs web-login ID tokens with HS256, keyed by the channel secret, while
  its discovery document advertises only ES256. So the `line` client is
  registered without discovery and allows HS256 only. The PRD has the exact
  registration. No new dependency.
- Schema change through `schema-check`:
  - new `users.line_user_id`, with a unique partial index;
  - `users.email` becomes optional (Google accounts only);
  - `email_1` becomes partial, so many email-less LINE accounts do not
    clash. `init_db()` rebuilds it once, so no migration script is needed;
  - a second insert path, for LINE sign-in;
  - `scripts/migrations/20261016_remove_username_only_users.py` is narrowed,
    so it never deletes LINE accounts. It has not run on production yet.
- Operations: a LINE Login channel (Web app) in the LINE Developers Console,
  with callback URLs for `localhost:5000`, `localhost:5001`, and the Heroku
  app. The channel never moves to another LINE provider, because LINE user
  IDs belong to the provider.
- Production rollout is part of this ticket:
  - set the Heroku config vars before the code reaches `main`, because
    `main` auto-deploys (`LP-0003`) and missing config crashes the dyno;
  - publish the channel;
  - smoke-test on Heroku.
- Manual checks use one LINE test account. The account-switch check stays
  Google-only. LINE's `disable_auto_login` after logout is covered by tests
  and one manual check.
- PRD: `docs/prd/LP-0009-line-login.md`. This is a new external integration
  with new routes and a schema change.
- No artifact — two stacked full-width buttons, Google first and LINE below,
  each per its brand guidelines. Decided by the user on 2026-10-17.
- Out of scope:
  - account linking or merging Google and LINE accounts;
  - LINE's email scope and email permission application;
  - LINE profile name or picture;
  - LIFF and LINE in-app browser auto-login;
  - the `bot_prompt` LINE Official Account friend prompt;
  - LINE messaging;
  - Apple sign-in;
  - any change to the Google flow beyond the shared logout flag.

## Acceptance Criteria

- [x] `/auth/login` shows the Google button, then the LINE button.
- [x] A LINE account with no `users` doc signs itself up. One doc is created
      with its `line_user_id`, one random name as both `username` and
      `display_name`, and no email, and it gets a session. Signing in again
      creates no second doc.
- [x] Two first LINE sign-ins racing on the same `sub` produce one account.
- [x] A Google account and a LINE account stay separate. Neither sign-in
      writes to the other's doc.
- [x] A refusal (cancel, bad `state`, token or ID-token failure, missing
      `sub`) shows 「登入失敗，請重試」 and writes nothing.
- [x] A LINE sign-in stores no LINE profile data and leaves `display_name`
      unchanged.
- [x] After logout, the next LINE sign-in shows LINE's login screen rather
      than signing in silently.
- [x] Startup fails, naming the variable, when `LINE_CLIENT_ID` or
      `LINE_CLIENT_SECRET` is missing.
- [x] Google sign-in behaves as before, and its existing tests pass unchanged.
- [x] `schema-check` passed. `data-model.md` lists:
      - `users.line_user_id` and `line_user_id_1`;
      - `email` as optional, with `email_1` partial;
      - both insert writers;
      - the narrowed LP-0002-01 migration.
- [x] `pytest` green — covered by `tests/test_auth.py` (LINE's token endpoint
      mocked, ID tokens signed locally with HS256) and
      `tests/test_migrations.py` (the `email_1` rebuild and the narrowed
      migration).
- [x] `flake8` clean.
- [x] Seen working in the running app: the LINE test account signs itself up
      against a local MongoDB, and the header shows `learner-…`. After logout,
      LINE shows its login screen. Signing in again leaves the database with
      one account for it.
- [x] Production: the Heroku config vars are set before the merge to `main`,
      and the channel is published. The LINE test account signs itself up
      through the `https://` callback on the `law-pass` app, and
      `init_db()` rebuilds `email_1` at boot. Release v13 (`db9dbbc`),
      2026-10-18: the test account signed up at 07:13 UTC (Heroku logs), and
      the user confirmed the channel is published. The first boot crashed
      once, because two gunicorn workers both ran the one-time `email_1` drop.
      The restart booted cleanly (see the `data-model.md` Change Log).
- [x] Docs synced: `docs/modules/auth/index.md` (rules, LINE flow, operations,
      manual checks), `docs/modules/db/data-model.md` (through
      `schema-check`), and `docs/modules/deploy/index.md` (config vars), plus
      a changelog entry.
- [x] Report at `docs/reports/LP-0009-line-login/report.md` is approved.

## Open Questions

- None.

## Resolution

Learners sign up and sign in with LINE below the Google button. Accounts are
keyed by the LINE `sub` in `users.line_user_id`, `email` is optional behind
partial unique indexes, and the feature is live on `law-pass` v13. Account
linking, LINE profile data, and a fix for the one-time worker race at first
boot were deliberately left out. See the
[changelog](../../changelog/2026-10-18-line-login.md) and the
[report](../../reports/LP-0009-line-login/report.md).

## Related Files

- `routes/auth.py`
- `services/auth.py`
- `app.py`
- `templates/login.html`
- `static/img/` (LINE icon from LINE's asset pack)
- `db/models.py`
- `scripts/migrations/20261016_remove_username_only_users.py`
- `.env.example`
- `tests/test_auth.py`
- `tests/test_app.py`
- `tests/test_migrations.py`
- `docs/prd/LP-0009-line-login.md`
- `docs/modules/auth/index.md`
- `docs/modules/db/data-model.md`
- `docs/modules/deploy/index.md`

## Handoff Appendix

### Settled Decisions

- LINE accounts are keyed by the LINE user ID (`sub`) in
  `users.line_user_id`, not by email. Decided by the user on 2026-10-17.
- No account linking: Google and LINE sign-ins make separate accounts.
  Decided by the user on 2026-10-17, with the identity key.
- Login page: the Google button stays first and LINE goes below, with no
  artifact. Decided by the user on 2026-10-17.
- Missing `LINE_CLIENT_ID` or `LINE_CLIENT_SECRET` fails startup, the same
  as Google's config. Decided by the user on 2026-10-17.
- This ticket runs the production rollout, with no separate cutover ticket.
  Decided by the user on 2026-10-17.
- One LINE test account for the manual checks. Decided by the user on
  2026-10-17.
- The PRD gap analysis's proposals were accepted by the user on 2026-10-17:
  - the env vars are named `LINE_CLIENT_*`;
  - HS256 verification through Authlib, registered without discovery;
  - `init_db()` rebuilds `email_1`;
  - the narrowed LP-0002-01 migration;
  - the proposed login copy.

### Behavior Details

- A race on the same new `sub` follows the Google pattern. The unique
  `line_user_id` index lets one insert win, and the loser finds that doc.
  A `username_1` clash redraws the random name.
- A LINE account has no email, so nothing downstream may assume
  `user['email']` holds a string. Today only `services/auth.py` reads it.

### Test Scenarios

- The PRD's Test Plan has the full list, for `tests/test_auth.py` and
  `tests/test_migrations.py`.
