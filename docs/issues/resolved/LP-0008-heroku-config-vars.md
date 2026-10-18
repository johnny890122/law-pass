---
id: LP-0008
title: Config vars for the new law-pass Heroku app
type: todo
status: resolved
priority: high
created: 2026-10-17
resolved: 2026-10-17
area: deploy
tags:
  - heroku
  - config
---

# Config vars for the new law-pass Heroku app

## Description

`LP-0003` created the `law-pass` app
(`https://law-pass-5ae90190d253.herokuapp.com`), but it has no config vars, so
its first deploy cannot reach production data. Split out of `LP-0003` at the
user's request on 2026-10-17, because the values live outside this checkout.

## Details

- Current:
  - `law-pass` (team `finder-experiment`) has no config vars.
  - Without `MONGO_URI`, `db/models.py` falls back to
    `mongodb://localhost:27017/patent_act`, so `init_db()` times out and the
    dyno crashes at boot.
  - The old production database is unreachable. The new `law-pass` Atlas
    cluster (project `johnny-personal`) holds only Atlas's `sample_mflix`.
- Desired: the app boots against a new, empty database with these vars
  set, and none committed:
  - `MONGO_URI`: the `law-pass` cluster's SRV string as Atlas user
    `law-pass-heroku`, with the database name in the path
    (`…mongodb.net/<db>?retryWrites=true&w=majority`). Atlas's Connect
    string ends in `/`, and PyMongo's `get_database()` in `db/models.py`
    then raises `ConfigurationError: No default database defined`. The
    name must not end in `_test`, which the tests reserve.
  - `SECRET_KEY`: a fresh random value, never the old app's.
  - ~~`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and
    `OPENROUTER_GRADING_MODEL`.~~ Deferred to `LP-0007` (see Deferred
    Decisions). The grading var is still required when they are set: the
    code default `anthropic/claude-3.5-haiku` is no longer listed on
    OpenRouter (checked 2026-10-17).
  - `FLASK_ENV=production`, so `app.py` marks the session cookie Secure.
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` belong to `LP-0007` step
  2, but the user set them on 2026-10-17. Google sign-in has been on `main`
  since then (`LP-0003`), so the running app uses them.
- No artifact — no screen changes.
- No PRD — ops setup with no code change.
- Out of scope: the old app's config, rotating any Atlas user (`LP-0007`
  step 5), the Google vars, and the OpenRouter vars (`LP-0007` step 10).

## Acceptance Criteria

- [x] `heroku config -a law-pass` lists `MONGO_URI`, `SECRET_KEY`, and
      `FLASK_ENV` (plus the Google vars), and no value appears in git.
      Rewritten 2026-10-17: `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`
      are deliberately unset until `LP-0002-05` lands, and move to `LP-0007`.
      "Not in git" was checked by pattern, not by value: no Atlas
      credential, Google client secret or ID, or OpenRouter key shape in any
      commit or tracked file, and `.env` is gitignored. Comparing the live
      values against git was not run, since the read of production secrets
      was not permitted.
- [x] The boot log shows no `ServerSelectionTimeoutError`, and
      `GET /health` returns 200. Checked 2026-10-17 on release v11
      (`62c45c9`): every boot from v7 to v11 reaches gunicorn `Listening`
      and `State changed … to up` with no error, on one Basic web dyno.
- [x] `pytest` and `flake8`: none — no code change.
- [x] Seen working in the running app: the login page loads at the new
      hostname. Opened with Playwright MCP at phone 390x844: the 「使用 Google
      帳戶登入」 button and 「第一次登入時會自動建立帳號」 render, and
      `/auth/login` answers 200. The only console error is the known
      `/favicon.ico` 404. The existing-user sign-in check stays with `LP-0003`.
- [x] Docs synced: `docs/modules/deploy/index.md` lists each var and where
      its value comes from, never the value, plus a changelog entry. One
      entry may cover `LP-0003` and this ticket.

## Open Questions

- None.

## Resolution

`law-pass` boots on its own Atlas database with `MONGO_URI`, `SECRET_KEY`,
and `FLASK_ENV` set, and `/health` and the login page answer 200 on v11.
The OpenRouter vars were deliberately left unset until `LP-0002-05` caps
grading, and moved to `LP-0007` step 10. See the
[changelog](../../changelog/2026-10-17-ci-and-heroku-app.md).

## Related Files

- `.env.example`
- `app.py`
- `db/models.py`
- `services/llm_client.py`
- `docs/modules/deploy/index.md`
- `docs/issues/resolved/LP-0003-heroku-ci-cd.md`
- `docs/issues/pending/LP-0007-google-sign-in-production-cutover.md`

## Handoff Appendix

### Settled Decisions

- The new app's `MONGO_URI` uses a new Atlas database user dedicated to
  law-pass, `law-pass-heroku`, with `readWrite` on its database only.
  Decided by the user on 2026-10-17.
- The database starts empty on the new `law-pass` cluster, because the old
  one is unreachable. Decided by the user on 2026-10-17.
- The user sets every value in the Heroku dashboard, from sources they
  hold. Claude guides and verifies key names, never values. Decided by the
  user on 2026-10-17.

### Behavior Details

- `heroku config:set` is outward-facing, so confirm before running it.
  Setting vars restarts the dyno.
- Atlas must admit Heroku's dynamic IPs: the `johnny-personal` project's
  Network Access needs `0.0.0.0/0`. A new project lists only its creator's
  IP. A `ServerSelectionTimeoutError` at boot points here first.

### Deferred Decisions

- **OpenRouter vars and which models** (was this ticket's Open Question).
  `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and `OPENROUTER_GRADING_MODEL`
  stay unset until `LP-0002-05`'s per-user grading cap lands, because
  self-signup would otherwise let anyone spend OpenRouter credit, uncapped.
  The empty database has no questions to grade yet. Moved to `LP-0007`
  step 10, where the model choice is made by the values the user sets.
  Decided by the user on 2026-10-17.
