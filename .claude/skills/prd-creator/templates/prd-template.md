---
ticket: LP-XXXX-YY
status: draft
created: YYYY-MM-DD
approved:
reviewer:
---

# PRD: Short ticket title

Implements `LP-XXXX-YY`, filed as `LP-XXXX-YY-<slug>.md` and listed in
[docs/issues/](../issues/README.md). Its folder follows its status. Behavior,
scope, and settled decisions live in the ticket and are not restated here.

## Before → After

One block per flow the story touches.

### Flow name

- **Before** (`docs/modules/<module>/index.md` § Section, or `path:line`):
  numbered steps as the code runs today. `None (new).` for a new flow.
- **After:** numbered steps as they will run.

## Route Contracts

### `METHOD /path`

- **Auth:** guard decorator, or `none`.
- **Request:** form, query, or JSON fields, with types.
- **Response:** status and redirect target, the template rendered, or the
  JSON shape.
- **Errors:** each failure case → status and what the user sees.

## Data Changes

Each change goes through `schema-check` at implementation. Nothing here is
final until that skill writes `docs/modules/db/data-model.md`.

| Collection | Change | Existing documents | Migration |
| --- | --- | --- | --- |
| `name` | Field or index added, changed, or removed | Conform, or need a backfill | `scripts/migrations/YYYYMMDD_<slug>.py`, or none |

## Templates and UI Copy

- `templates/<file>.html`: what changes.
- Copy, quoted verbatim: 「現有文案」 → 「新文案」 (proposed).

## LLM Prompts

`None — <reason>.` or: the prompt file, the change, the model, and the
expected output shape.

## Business Rules and Edge Cases

| ID | Rule or scenario | Expected behavior |
| --- | --- | --- |
| BR-1 | | |

## Test Plan

OpenRouter and every other external call are mocked.

- `tests/test_<area>.py`
  - Scenario: setup → action → expected response and collection change.

## Rollout and Migration

- Env vars and config to set locally and on Heroku.
- Ordered steps around the deploy: migrations, backfills, cutover.
- Rollback: what to revert, and whether data must be restored.

## Implementation Order

1. A step that leaves `pytest` green.
