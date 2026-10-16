---
id: LP-XXXX
title: Short ticket title
type: bug|feature|improvement|refactor|todo|epic|story
status: pending
priority: high|medium|low
created: YYYY-MM-DD
resolved:
area: short-area
tags:
  - tag
# Stories only: parent epic id, and the story id extends it (LP-XXXX-01).
# parent: LP-XXXX
---

# Short ticket title

## Description

One or two sentences: who needs what, and why now.

## Details

- Current behavior → desired behavior.
- Scope: which routes, services, templates, and Mongo collections.
- `No artifact — <reason>.` or the visual question the variants must answer.
- Stories and features only: `No PRD — <reason>.` or
  `PRD: docs/prd/LP-XXXX-<slug>.md`.
- Out of scope: what this ticket should not do.

## Acceptance Criteria

- [ ] Verifiable done condition.
- [ ] `pytest` green — covered by `tests/test_....py`.
- [ ] `flake8` clean.
- [ ] Seen working in the running app: what to open and what to observe.
- [ ] Docs synced: `docs/modules/<module>/index.md` and a changelog entry.
- [ ] PRD tickets only: report at `docs/reports/LP-XXXX-<slug>/report.md` is approved.

## Open Questions

- What needs a human answer before implementation? Write `- None.` once cleared.

## Related Files

- `path/to/file`

## Handoff Appendix

Use only when the discussion holds implementation-critical detail that should
not be compressed away.

### Settled Decisions

- Concrete decisions from the discussion.

### Behavior Details

- Route, request, template rendered, what the user sees, which collection
  fields change.

### Data And LLM Notes

- Collections, fields, indexes, prompts, model choice, cost or latency limits.

### Test Scenarios

- Target test modules and scenario bullets.

### Deferred Decisions

- Details intentionally left for a later ticket.
