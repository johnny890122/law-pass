---
id: LP-0001
title: Infra skills for schema changes, design variants, PRDs, and PRD reports
type: epic
status: resolved
priority: medium
created: 2026-10-16
resolved: 2026-10-17
area: docs
tags:
  - skills
  - infra
---

# Infra skills for schema changes, design variants, PRDs, and PRD reports

## Description

The ticket-first workflow in `CLAUDE.md` names the stages but not how three of
the riskier ones get done. This epic adds a project skill for each: schema
changes (data integrity and migrations), frontend variant builds (stage 2
artifacts), implementation PRDs for big feature stories, and the audit
report that closes a PRD-backed ticket.

## Details

- Current: `ticket-system` is the only project skill. Schema changes have no
  checklist or migration convention, the artifact contract lives only as
  prose in `CLAUDE.md`, and nothing sits between a big story and its code.
- Desired: four more skills under `.claude/skills/`, each referenced from
  `CLAUDE.md` at the point in the workflow where it applies.
- Roadmap:
  - `LP-0001-01` `schema-check` skill, which writes
    `docs/modules/db/data-model.md` (the schema's single source of truth)
    only after confirming a change is safe. A drift test forces it to run
    (`db`).
  - `LP-0001-02` `design-variants` skill, a lean port of moblab's
    `claude-design` (`ui`).
  - `LP-0001-03` `prd-creator` skill, a lean port of moblab's `prd-creator`.
    When the ticket calls for one, it writes an exact implementation PRD to
    `docs/prd/` (`docs`).
  - `LP-0001-04` `prd-report` skill. It writes a plain-language audit report
    of an implemented PRD, with screenshots of the user journey, to
    `docs/reports/`. The user's sign-off on it is the closing gate of a
    PRD-backed ticket (`docs`).
- No artifact. These tickets build tooling, and no screen choice is involved.
- Out of scope: retiring `docs/requirements.md`, `docs/design.md`, and
  `docs/tasks.md` (that has its own pending ticket per `CLAUDE.md`); a
  design-token or design-system skill.

## Acceptance Criteria

- [x] All child stories are `resolved` or `wont_fix`. All four are
      `resolved`.
- [x] `CLAUDE.md` names all four skills where the workflow invokes them.
- [x] `pytest` green: covered by the child stories. 70 passed on
      2026-10-17.
- [x] `flake8` clean: covered by the child stories. Clean on 2026-10-17.
- [x] Seen working: covered by each child story's smoke run.
- [x] Docs synced: covered by the child stories' changelog entries.

## Open Questions

- None.

## Resolution

Four skills now sit at the risky points of the workflow. `schema-check`
gates schema changes, `prd-creator` writes implementation PRDs, and
`prd-report` writes the closing audit. The stage 2 artifact skill was
`design-variants`, and LP-0004-02 has since replaced it with `neta-design`.
See the changelog entries:
[schema-check](../../changelog/2026-10-16-schema-check.md),
[design-variants](../../changelog/2026-10-16-design-variants-skill.md),
[prd-creator](../../changelog/2026-10-16-prd-creator-skill.md), and
[prd-report](../../changelog/2026-10-16-prd-report-skill.md).

## Related Files

- `CLAUDE.md`
- `.claude/skills/`
- `docs/issues/*/LP-0001-infra-skills/`
