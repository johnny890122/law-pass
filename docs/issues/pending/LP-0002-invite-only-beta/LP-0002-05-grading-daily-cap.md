---
id: LP-0002-05
title: Per-user daily cap on LLM grading
type: story
status: pending
priority: high
created: 2026-10-17
resolved:
area: grading
parent: LP-0002
tags:
  - cost
  - openrouter
---

# Per-user daily cap on LLM grading

## Description

With self-signup (`LP-0002-01`), any Google account can submit short answers,
and each one is graded by OpenRouter on the platform key. A per-user daily cap
bounds that spend before production self-signup opens.

## Details

- Current: `POST /api/quiz/session/<session_id>/answer` (`routes/quiz.py:201`)
  grades a `ShortAnswer` with `grader_service.grade_answer`
  (`routes/quiz.py:306`, `services/grader.py`), one OpenRouter call per
  submission, with no limit. `MCQ` answers are graded locally and cost
  nothing.
- Desired:
  - Each user gets a cap on LLM-graded answers per UTC day.
  - At the cap, a `ShortAnswer` submission makes no OpenRouter call and
    writes no score, and the quiz tells the learner why.
  - `MCQ` grading is never capped.
  - How the daily count is kept (a new field, or counted from existing
    answers) is the implementer's call. A new field or collection goes
    through `schema-check`.
- Ordering: production self-signup from `LP-0002-01` opens only after this
  story lands. `LP-0002-01`'s code can be built and tested locally before
  then.
- No PRD — one guard in one route, and Details states the contract once the
  Open Questions are answered.
- No artifact — the at-cap message uses the quiz page's existing error area.
- Out of scope: caps on question generation (admin-only per `LP-0002-03`),
  billing, per-user keys (BYOK), and a usage dashboard.

## Acceptance Criteria

- [ ] A user at the cap submits a `ShortAnswer`. No OpenRouter call is made,
      no score is written, and the response explains the cap.
- [ ] Below the cap, `ShortAnswer` grading works as today. `MCQ` grading
      ignores the cap.
- [ ] The count resets at the UTC day boundary.
- [ ] `pytest` green — covered by `tests/test_grading_cap.py`, with the grader
      mocked and no OpenRouter calls.
- [ ] `flake8` clean.
- [ ] Seen working in the running app: with the cap lowered for the run, the
      next `ShortAnswer` past it shows the cap message.
- [ ] Docs synced: `docs/modules/grading/index.md` (new),
      `docs/modules/index.md`, and `docs/modules/db/data-model.md` if a field
      is added (through `schema-check`), plus a changelog entry.

## Open Questions

- What is the cap: how many LLM-graded answers per user per UTC day?
- What exactly happens at the cap: is the answer refused outright, or saved
  ungraded (graded later, or shown with the reference answer)? And what copy
  does the learner see?
- Is the admin (`LP-0002-03`'s `is_admin`) exempt?

## Related Files

- `routes/quiz.py`
- `services/grader.py`
- `templates/quiz_session.html`
- `tests/test_grading_cap.py` (new)
- `docs/modules/db/data-model.md`

## Handoff Appendix

### Settled Decisions

- The cap is per user per day, filed as its own story, and production
  self-signup waits for it. Decided by the user on 2026-10-17.
