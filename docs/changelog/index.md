# Changelog

One entry per landing, newest first.

| File | LP ids | Summary |
| --- | --- | --- |
| [2026-10-17-ci-and-heroku-app.md](2026-10-17-ci-and-heroku-app.md) | LP-0003 | GitHub Actions runs `flake8` and `pytest` on every push and PR; the new `law-pass` Heroku app auto-deploys `main` after CI passes; config vars split to LP-0008. |
| [2026-10-16-prd-report-skill.md](2026-10-16-prd-report-skill.md) | LP-0001-04 | `prd-report` skill writes a plain-language audit report with screenshots to `docs/reports/`; the user's sign-off on it is the closing gate of a PRD-backed ticket. |
| [2026-10-16-schema-check.md](2026-10-16-schema-check.md) | LP-0001-01 | `schema-check` skill gates schema changes; `docs/modules/db/data-model.md` is the schema's source of truth, enforced by `tests/test_schema_drift.py`; `init_db()` fails loudly on a blocked unique index. |
| [2026-10-16-prd-creator-skill.md](2026-10-16-prd-creator-skill.md) | LP-0001-03 | `prd-creator` skill writes implementation PRDs to `docs/prd/` for big stories; conditional stage 1b and PRD Call wired into `CLAUDE.md` and `ticket-system`. |
| [2026-10-16-design-variants-skill.md](2026-10-16-design-variants-skill.md) | LP-0001-02 | `design-variants` skill builds stage 2 artifacts; `CLAUDE.md` Artifacts trimmed to the contract. |
