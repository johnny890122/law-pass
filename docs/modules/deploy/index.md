# Deploy

Where law-pass runs and how code reaches it. Current truth since
[LP-0003](../../changelog/2026-10-17-ci-and-heroku-app.md).

## Product rules

- **`main` is production.** Heroku's GitHub integration deploys every push
  to `main` of `johnny890122/law-pass` to the `law-pass` app, and only after
  CI passes ("Wait for CI to pass"). A merge to `main` is a release. GitHub
  holds no Heroku API key.
- **CI gates every push and pull request.** `.github/workflows/ci.yml` runs
  `flake8`, then `pytest`, on the Python in `.python-version`, against a
  MongoDB 7 service container on `localhost:27017`. It needs no secrets.
  OpenRouter and Google are mocked, and the tests default `MONGO_URI` to
  `patent_act_test`, which the `_test` guards in the tests require.
- **One Python version.** `.python-version` drives both CI and Heroku's
  buildpack. If the buildpack lacks the patch release, pin `3.11` rather
  than let them diverge.
- **Migrations are manual.** `Procfile` has no `release:` phase. A migration
  runs from a local checkout against production, after a dump.
- **Indexes build at boot.** `create_app()` runs `init_db()`, so a blocked
  unique index crashes the dyno after the release, not the build. Read
  `heroku logs` after every deploy.
- **Google sign-in waits for its cutover.** `3c1dcd8` on `infra`
  (LP-0002-01) merges to `main` only at LP-0007 step 7. Before the
  migration, `email_1` cannot build over production users that have no
  email, and the grading cap (LP-0002-05) must land first.

## Apps

| App | Team | URL | Deploys from | Status |
| --- | --- | --- | --- | --- |
| `law-pass` | `finder-experiment` | <https://law-pass-5ae90190d253.herokuapp.com> | `johnny890122/law-pass` `main`, automatic | Production. Basic dyno. |
| `patent-act-15774ac83829` | Not visible to the CLI login | <https://patent-act-15774ac83829.herokuapp.com> | `johnny890122/patent_act` | Old. Left running until LP-0007 cuts it off. |

Google OAuth redirect URI for this app, registered at LP-0007 step 1:
`https://law-pass-5ae90190d253.herokuapp.com/auth/google/callback`.

## Config vars

Names and sources only. Values are never committed.

| Var | Value comes from | Set by |
| --- | --- | --- |
| `MONGO_URI` | The production Atlas database, the same one the old app uses | LP-0008 |
| `SECRET_KEY` | A fresh random value. Rotating it ends every session. | LP-0008. Rotated at LP-0007 step 8. |
| `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | OpenRouter. `OPENROUTER_GRADING_MODEL` is optional. | LP-0008 |
| `FLASK_ENV` | `production`, which makes the session cookie Secure | LP-0008 |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | The Google OAuth client. `create_app()` refuses to start without them once Google sign-in deploys. | LP-0007 step 2 |

## Operations

- Dashboard → `law-pass` → Deploy → GitHub: connect
  `johnny890122/law-pass`, enable automatic deploys from `main`, and check
  "Wait for CI to pass".
- Dyno type: `heroku ps:type web=basic -a law-pass`, once the first build
  creates the `web` process.
- Logs: `heroku logs --tail -a law-pass`. Rollback:
  `heroku releases:rollback -a law-pass`.

## Code

- `.github/workflows/ci.yml`: the CI job.
- `Procfile`, `.python-version`, `requirements.txt`: the Heroku build inputs.
