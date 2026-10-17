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
  - The production `MONGO_URI` is only in the old
    `patent-act-15774ac83829` app and in Atlas. The CLI login
    (`b07303058@ntu.edu.tw`) cannot see the old app, and the local `.env`
    points at a local MongoDB.
- Desired: the app boots against the production Atlas database with these
  vars set, and none committed:
  - `MONGO_URI`: the same Atlas database production uses today (`LP-0003`
    settled decision).
  - `SECRET_KEY`: a fresh random value, never the old app's.
  - `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`. `OPENROUTER_GRADING_MODEL`
    is optional, because `services/llm_client.py` holds the defaults.
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
- [ ] The old `patent-act-15774ac83829` app still serves.
- [ ] `pytest` and `flake8`: none — no code change.
- [ ] Seen working in the running app: the login page loads at the new
      hostname. The existing-user sign-in check stays with `LP-0003`.
- [ ] Docs synced: `docs/modules/deploy/index.md` lists each var and where
      its value comes from, never the value, plus a changelog entry. One
      entry may cover `LP-0003` and this ticket.

## Open Questions

- Which Atlas database user does the new `MONGO_URI` use? A new user
  dedicated to law-pass lets `LP-0007` step 5 rotate the old app's user
  without cutting off the new app. Reusing the old app's URI as-is makes
  step 5 create that user first.
- Who sets each value, and from where? The production `MONGO_URI` is
  reachable only through the old app's dashboard or Atlas. Is
  `OPENROUTER_API_KEY` the old app's key or the local `.env` key?
- `OPENROUTER_MODEL` (and the grading model): the values production runs
  today, or the code defaults (`anthropic/claude-sonnet-4.5` and
  `anthropic/claude-3.5-haiku`)?

## Related Files

- `.env.example`
- `app.py`
- `db/models.py`
- `services/llm_client.py`
- `docs/modules/deploy/index.md`
- `docs/issues/in_progress/LP-0003-heroku-ci-cd.md`
- `docs/issues/pending/LP-0007-google-sign-in-production-cutover.md`

## Handoff Appendix

### Behavior Details

- `heroku config:set` is outward-facing, so confirm before running it.
  Setting vars restarts the dyno.
- Atlas must admit Heroku's dynamic IPs. The old Heroku app already reaches
  the cluster, so its IP access list likely allows it. A
  `ServerSelectionTimeoutError` at boot points here first.
