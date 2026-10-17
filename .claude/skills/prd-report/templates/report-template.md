---
ticket: LP-XXXX-YY
prd: docs/prd/LP-XXXX-YY-<slug>.md
status: draft
created: YYYY-MM-DD
approved:
reviewer:
---

# Report: Short ticket title

- **Ticket:** `LP-XXXX-YY`, listed in [docs/issues/](../../issues/README.md).
- **PRD:** [LP-XXXX-YY-&lt;slug&gt;](../../prd/LP-XXXX-YY-<slug>.md)
- **Changelog:** [YYYY-MM-DD-&lt;slug&gt;](../../changelog/YYYY-MM-DD-<slug>.md)
- **Verified at:** commit `abc1234`.
- **Environment:** the app run locally with `python app.py`, database
  `lp_report_<id>` on a local MongoDB, provisioned test Google account
  `<name>` added with `scripts/add_user.py`. Seed data (stand-in): what was added and why the
  journey needs it.
- **Prepared by:** Claude, YYYY-MM-DD.

## Summary

Three to five plain sentences on what changed for the user.

## User Journey

The happy path, one step per user action, on a phone (390x844).

### 1. Step name

![What the screen shows](shots/01-<step>-phone.png)

The user does this and sees 「verbatim copy」.

## Edge Cases

| PRD row | Scenario | What the user sees | Evidence | Result |
| --- | --- | --- | --- | --- |
| BR-1 | In plain words | 「verbatim copy」 | [screenshot](shots/NN-<case>-phone.png) | Pass |
| BR-2 | In plain words | What would happen | `tests/test_<area>.py::test_name` (test only) | Pass |

## API Changes

| Method and path | Who can call it | What it does | Change |
| --- | --- | --- | --- |
| `METHOD /path` | Signed-in users | In plain words | New, changed, or removed |

## Database Changes

| Collection | What changed | Existing data | Migration | Where it ran |
| --- | --- | --- | --- | --- |
| `name` | In plain words | What happened to records already there | The script, or none | Locally, and on production or "not yet run on production" |

## Deviations From the PRD

- None.

## How It Was Verified

- Automated tests: N passed, 0 failed (`pytest`).
- Code style check: clean (`flake8`).
- The app: run locally as in Environment, and driven in a browser with
  Playwright at phone size, with no console errors.
