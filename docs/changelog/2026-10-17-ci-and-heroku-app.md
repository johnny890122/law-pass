# 2026-10-17 — CI on GitHub Actions, and the law-pass Heroku app

**LP ids:** LP-0003, LP-0008

Nothing tested or deployed `main`, and the only production app was the old
`patent-act-15774ac83829`, which the current Heroku login cannot see. Now
every push and pull request runs `flake8` and `pytest` on GitHub Actions, and
the new `law-pass` app deploys `main` once CI passes. Rules live in
[`docs/modules/deploy/index.md`](../modules/deploy/index.md).

| Area | Was | Now |
| --- | --- | --- |
| CI | None. `requirements.txt` named a CI that did not exist. | `.github/workflows/ci.yml` runs on every push and PR, with a MongoDB 7 service container and no secrets. |
| Production app | `patent-act-15774ac83829`, deployed from the old `patent_act` repo. | `law-pass` in team `finder-experiment`, at `https://law-pass-5ae90190d253.herokuapp.com`, deployed from `johnny890122/law-pass` `main` after CI passes. |
| Production data | The old app's Atlas database. | A new, empty database on the `law-pass` Atlas cluster. The old one is unreachable, so users, progress, laws, and questions do not carry over. |
| `main` | The initial commit, failing `flake8`. | `488a21b` (LP-0001, with the lint fixes), the LP-0003 commits, and `infra` merged for a production test of Google sign-in (LP-0002-01). |
| README | Linked the old repo and app. | Links the new repo and app. |
| Config vars (LP-0008) | None, so the dyno could not reach a database. | `MONGO_URI` (its own Atlas user), a fresh `SECRET_KEY`, `FLASK_ENV=production`, and the Google vars. Boots clean, and `/health` answers 200 on v11. |

## Deliberately not done

- The OpenRouter vars (LP-0008). They stay unset until LP-0002-05's
  per-user grading cap is deployed, so self-signup cannot spend credit
  uncapped. Until then, grading and generation fail on Heroku. LP-0007
  step 10 sets them.
- Loading laws and questions into the new database. The repo has no loader
  for real law text.
- A `release:` phase. Migrations stay manual.
- Staging or review apps, branch protection, deploy notifications, and
  `heroku.yml` container deploys.
- Touching the old app. It shares no data with `law-pass`.
