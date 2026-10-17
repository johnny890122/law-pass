---
id: LP-0008
title: Config vars for the new law-pass Heroku app
type: todo
status: pending
priority: high
created: 2026-10-17
resolved:
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
  - `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and `OPENROUTER_GRADING_MODEL`.
    The grading var is required: the code default
    `anthropic/claude-3.5-haiku` is no longer listed on OpenRouter
    (checked 2026-10-17), so grading fails without it.
  - `FLASK_ENV=production`, so `app.py` marks the session cookie Secure.
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are not set here. They
  belong to `LP-0007` step 2, because the code deployed by `LP-0003` still
  uses username login.
- No artifact — no screen changes.
- No PRD — ops setup with no code change.
- Out of scope: the old app's config, rotating any Atlas user (`LP-0007`
  step 5), and the Google vars.

## Acceptance Criteria

- [ ] `heroku config -a law-pass` lists `MONGO_URI`, `SECRET_KEY`,
      `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and `FLASK_ENV`, and no
      value appears in git.
- [ ] The boot log shows no `ServerSelectionTimeoutError`, and
      `GET /health` returns 200.
- [ ] `pytest` and `flake8`: none — no code change.
- [ ] Seen working in the running app: the login page loads at the new
      hostname. The existing-user sign-in check stays with `LP-0003`.
- [ ] Docs synced: `docs/modules/deploy/index.md` lists each var and where
      its value comes from, never the value, plus a changelog entry. One
      entry may cover `LP-0003` and this ticket.

## Open Questions

- Which models: `OPENROUTER_MODEL` (the default
  `anthropic/claude-sonnet-4.5` is still listed) and
  `OPENROUTER_GRADING_MODEL` (the default is gone)? Answered by the values
  the user sets.

## Related Files

- `.env.example`
- `app.py`
- `db/models.py`
- `services/llm_client.py`
- `docs/modules/deploy/index.md`
- `docs/issues/in_progress/LP-0003-heroku-ci-cd.md`
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
