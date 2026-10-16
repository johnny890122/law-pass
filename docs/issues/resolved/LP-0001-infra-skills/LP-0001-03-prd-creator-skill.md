---
id: LP-0001-03
title: PRD-creator skill for big feature stories
type: story
status: resolved
priority: medium
created: 2026-10-16
resolved: 2026-10-16
area: docs
parent: LP-0001
tags:
  - skills
  - prd
---

# PRD-creator skill for big feature stories

## Description

A feature starts as an epic with a series of stories (e.g. `LP-0002`). A
story says what to build and why, but a big one also needs an exact
implementation spec before code starts. A `prd-creator` skill, ported lean
from moblab, writes that spec as a PRD the story links to.

## Details

- Current: `ticket-system` grounds a requirement and writes the story:
  behavior, scope, and settled decisions. Nothing sits between the story and
  the code. Big stories such as `LP-0002-01` pack implementation detail into
  `## Details` and the Handoff Appendix, and nothing spells out the exact
  contracts, data changes, or build order.
- Desired: `.claude/skills/prd-creator/SKILL.md` plus one
  `templates/prd-template.md`, ported from
  `/Users/johnnychang/moblab/prd-creator/.gemini/skills/prd-creator/`
  (Workflow A only):
  - **Trigger gate:** the ticket's Details says a PRD is required, or the user
    asks for one. It does not trigger for bug fixes, small improvements,
    tooling, or docs tickets.
  - **Split with the ticket:** the ticket owns *what* and *why*. The PRD owns
    *exactly how*. A PRD never reopens a settled decision. A new question
    found while writing goes into the ticket's `## Open Questions`, so the
    existing gate blocks `in_progress`. The skill never answers it.
  - **Read order:** the story, its epic, the owning
    `docs/modules/<module>/index.md` (read-only here, like moblab's
    handbook), `docs/modules/db/data-model.md`, and the code the story
    touches.
  - **Steps, each pausing for the user:**
    1. Gap analysis: list the routes, services, collections, templates,
       prompts, and tests the story affects, and the conflicts or missing
       edge cases found.
    2. Draft `docs/prd/<ticket-id>-<slug>.md` from the template.
    3. Review until the user approves. The PRD's `status` becomes `approved`.
  - **PRD sections:** a link to the ticket (no restating), Before → After per
    flow (Before cites the module doc or `file:line`), route contracts
    (method, path, auth, request, response, errors), data changes (handed to
    the `schema-check` skill, not decided here), templates and UI copy
    (Chinese quoted verbatim), LLM prompts when touched, business rules and
    edge cases, a test plan per `tests/test_<area>.py` with OpenRouter
    mocked, rollout and migration, and implementation order.
- **Workflow wiring:**
  - `CLAUDE.md` gains a conditional PRD stage between Ticket and Artifact,
    plus `prd/` in the Docs tree.
  - `ticket-system` gains a "PRD Call" section, parallel to Artifact Call.
    Every story or feature ticket carries one Details bullet: the PRD path,
    or `No PRD — <reason>.`
  - `assets/TICKET_TEMPLATE.md` gains that bullet.
  - A ticket that needs a PRD moves to `in_progress` only once its PRD is
    `approved`.
- **Lifecycle:** the PRD joins the sync chain. Code that diverges from it is
  a defect in both, per `CLAUDE.md`. Once the ticket resolves, the PRD is a
  historical record. Its rules are folded into the module doc during doc
  sync, and the module doc stays current truth.
- Dropped from the reference:
  - Workflow B (handbook update), because stage 4 doc sync already covers it.
  - The product-handbook onboarding, `product-line-profile.yaml`, and
    variations, because there is one product.
  - The comparison/merged template pair. A single template is enough, and
    Before reads "None (new)" for new flows.
  - `context.md` sessions, because the ticket holds decisions and sources.
  - The BE/FE ticket split, Jira links, metrics, and the `[Status: …]` footer.
- No artifact. This story builds tooling, and no screen choice is involved.
- Out of scope:
  - Writing PRDs for existing tickets. The `LP-0002` stories get their PRD
    call when each is refined before `in_progress`.
  - Having the generator enforce PRD approval.
  - A `docs/prd/` index, because each ticket links its own PRD.

## Acceptance Criteria

- [x] `.claude/skills/prd-creator/SKILL.md` and `templates/prd-template.md`
      cover the trigger gate, ticket/PRD split, read order, three paused
      steps, PRD sections, and lifecycle above. They contain no handbook,
      onboarding, Jira, or BE/FE references.
- [x] `CLAUDE.md` shows the conditional PRD stage and `docs/prd/` in the Docs
      tree. `ticket-system` has a PRD Call section, and the ticket template
      carries the PRD bullet.
- [x] `pytest` green: no code or test change. The box stays to confirm
      nothing regressed. 27 passed.
- [x] `flake8` clean: no Python changed. The 7 pre-existing violations in
      `services/inventory.py`, `services/progress.py`, and
      `tests/test_progress_service.py` were fixed in a separate lint change.
- [x] Seen working: following the skill on `LP-0002-01` produced a gap
      analysis, a draft PRD in `docs/prd/`, and a review pause. Note: the
      keep-or-delete call on that draft belongs to `LP-0002-01`, not this
      story. The user ruled it out of scope here on 2026-10-16, so
      `docs/prd/LP-0002-01-google-sign-in.md` is left untouched at
      `status: draft`.
- [x] Docs synced: `CLAUDE.md`, `ticket-system`, and a changelog entry. No
      module doc applies, because no product behavior changes.

## Open Questions

- None.

## Related Files

- `/Users/johnnychang/moblab/prd-creator/.gemini/skills/prd-creator/`
  (reference, external)
- `/Users/johnnychang/moblab/prd-creator/prd-sessions/PRD-paypal-payer-id-uniqueness/`
  (example output, external)
- `.claude/skills/prd-creator/` (new)
- `.claude/skills/ticket-system/SKILL.md`
- `.claude/skills/ticket-system/assets/TICKET_TEMPLATE.md`
- `.claude/skills/schema-check/SKILL.md`
- `CLAUDE.md`
- `docs/prd/` (new)

## Handoff Appendix

### Settled Decisions

- PRDs live at `docs/prd/<ticket-id>-<slug>.md`, outside `docs/issues/`. The
  generator parses every `.md` under `docs/issues/` as a ticket, and this
  path survives status changes. Decided by the user on 2026-10-16.
- The ticket makes the PRD call. Big features get a PRD, and bug fixes and
  small improvements rely on the ticket alone. Decided by the user on
  2026-10-16.
- Skill name is `prd-creator`, as the user named it.
- Stage numbering: the PRD stage is `1b` rather than a renumbered `2`,
  because stage numbers are cited in `ticket-system`, `design-variants`, and
  a landed changelog entry.
- Gap analysis splits "how" gaps (proposed and confirmed at the step 1
  pause) from "what or why" gaps (sent to the ticket's Open Questions). The
  `LP-0002-01` smoke run showed that most PRD gaps are "how".

### Deferred Decisions

- Generator enforcement of PRD approval (parse the PRD's `status` before
  allowing `in_progress`). File it if the manual gate gets skipped in
  practice.

## Resolution

Landed the `prd-creator` skill and its template, the conditional stage 1b in
`CLAUDE.md`, and the PRD Call in `ticket-system` and the ticket template.
Deliberately not done: generator enforcement of PRD approval, and PRDs for
other tickets. The `LP-0002-01` smoke-run draft stays with that story. Full
story in [2026-10-16-prd-creator-skill](../../../changelog/2026-10-16-prd-creator-skill.md).
