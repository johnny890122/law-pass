---
id: LP-0003
title: CI on GitHub Actions and auto-deploy to a new law-pass Heroku app
type: improvement
status: in_progress
priority: high
created: 2026-10-16
resolved:
area: deploy
tags:
  - ci
  - heroku
---

# CI on GitHub Actions and auto-deploy to a new law-pass Heroku app

## Description

`LP-0002-01` registers `https://<app>.herokuapp.com/auth/google/callback` with
Google, but no Heroku app is reachable from this repo, and nothing tests or
deploys `main`. Before Google sign-in cuts over, the admin needs a known
production hostname and a pipeline that ships `main` only when `pytest` and
`flake8` pass.

## Details

- Current:
  - No `.github/workflows/`. `requirements.txt` labels its test block "also
    installed in CI", but no CI exists.
  - Production is `patent-act-15774ac83829.herokuapp.com` (README), deployed
    from the old `johnny890122/patent_act` repo. The logged-in `heroku` CLI
    account cannot see it.
  - The deploy inputs already exist: `Procfile` (`web: gunicorn app:app`),
    `.python-version` (`3.11.15`), and `requirements.txt`. `init_db()` builds
    indexes at boot.
  - `tests/test_app.py` and `tests/test_schema_drift.py` need a real MongoDB
    at `localhost:27017` (`patent_act_test`).
- Desired:
  - `.github/workflows/ci.yml` runs on every push and pull request. It takes
    Python from `.python-version`, runs `pip install -r requirements.txt`,
    `flake8`, and then `pytest`, with a MongoDB service container on `27017`.
    It needs no secrets, since OpenRouter stays mocked.
  - A new Heroku app for law-pass runs on a Basic dyno with the Python
    buildpack. Its exact `https://<name>-<hash>.herokuapp.com` hostname is
    recorded in `docs/modules/deploy/index.md`, and that is the redirect URI
    `LP-0002-01` registers.
  - Config vars are set under `LP-0008`, split out on 2026-10-17 at the
    user's request. `MONGO_URI` points at the same Atlas database that
    production uses today, and none are committed.
  - `main` is production once auto-deploy is on. It takes `488a21b`
    (LP-0001, with the lint fixes) and the LP-0003 commit. `3c1dcd8`
    (LP-0002-01 Google sign-in) stays on `infra` until `LP-0007` step 7.
    `init_db()` would otherwise build the unique `email_1` index over
    production users without an email, and the app would fail to boot.
  - Heroku's GitHub integration connects `johnny890122/law-pass` and
    auto-deploys `main` with "Wait for CI to pass" on.
  - The README's GitHub URL and production URL point at the new repo and app.
- Migrations stay manual. The `LP-0002-01` PRD's Rollout runs them from a
  local checkout, with a dump first. `Procfile` gets no `release:` phase.
- No artifact — no screen changes.
- No PRD — deploy tooling: one workflow file plus dashboard settings.
- Out of scope:
  - The old `patent-act-15774ac83829` app is left running and untouched. Its
    username-login risk after `LP-0002-01` lands is tracked in that ticket's
    Open Questions.
  - Staging or review apps, branch protection, and deploy notifications.
  - `heroku.yml` and container deploys.

## Acceptance Criteria

- [ ] Every push and PR runs `.github/workflows/ci.yml`, and a commit with a
      `flake8` error fails it (shown on a throwaway branch).
- [ ] The new Heroku app exists on a Basic dyno. Its config vars and the
      `MONGO_URI` that reaches production Atlas are `LP-0008`'s.
- [ ] A push to `main` deploys to the new app only after CI passes, and
      Heroku's activity feed ties the build to that commit.
- [ ] `GET /health` on the new hostname returns 200 after the first
      auto-deploy, which needs `LP-0008` landed.
- [ ] `pytest` green in CI and locally — no new test. The workflow runs the
      existing suite.
- [ ] `flake8` clean.
- [ ] Seen working in the running app: open the new hostname with Playwright
      MCP, and see the login page load and an existing user sign in.
- [ ] Docs synced: `docs/modules/deploy/index.md` (new),
      `docs/modules/index.md`, the README URLs, and a changelog entry.

## Open Questions

- None.

## Related Files

- `.github/workflows/ci.yml` (new)
- `Procfile`
- `.python-version`
- `requirements.txt`
- `tests/test_app.py`
- `tests/test_schema_drift.py`
- `README.md`
- `docs/modules/deploy/index.md` (new)
- `docs/modules/index.md`
- `docs/prd/LP-0002-01-google-sign-in.md`

## Handoff Appendix

### Settled Decisions

- A new Heroku app for law-pass, not the old `patent-act-15774ac83829`.
  Decided by the user on 2026-10-16.
- Heroku's GitHub integration auto-deploys `main` with "Wait for CI to
  pass". GitHub Actions does CI only, and GitHub holds no Heroku API key.
  Decided by the user on 2026-10-16.
- `MONGO_URI` points at the same Atlas database as today, so nothing is
  copied. Decided by the user on 2026-10-16.
- The old app is left alone. Decided by the user on 2026-10-16.
- The app is `law-pass` in the `finder-experiment` Heroku team, not
  `moblab-research`, at `https://law-pass-5ae90190d253.herokuapp.com`.
  Decided by the user on 2026-10-17.
- Config vars move to `LP-0008`. Decided by the user on 2026-10-17.
- `main` takes `488a21b` plus the LP-0003 commit, and Google sign-in stays
  off `main` until `LP-0007`. Decided by the user on 2026-10-17.
- Basic dyno, so the app never sleeps. Decided by the user on 2026-10-16.

### Behavior Details

- The dashboard steps are the user's: the GitHub OAuth connection in the
  Heroku dashboard, and enabling auto-deploy of `main` with "Wait for CI to
  pass". The CLI login `b07303058@ntu.edu.tw` is a `finder-experiment` admin.
- Heroku's "Wait for CI" waits on GitHub commit statuses, and its docs never
  mention GitHub Actions, which reports check runs. The first auto-deploy
  must show the build starting only after CI finished. If it starts sooner,
  CI has to post a commit status, which this ticket then adds.
- If the buildpack does not offer `3.11.15`, pin `.python-version` to `3.11`
  rather than diverging CI from Heroku.
- CI keeps the default `patent_act_test` database, so the `_test` guard in
  `tests/test_schema_drift.py` holds.
- Ordering: this ticket lands before `LP-0002-01` Rollout step 1, which
  registers the new hostname with Google.
