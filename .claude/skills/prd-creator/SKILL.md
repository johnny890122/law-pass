---
name: prd-creator
description: "Write the implementation PRD for a big `LP-XXXX` feature story: gap analysis against the code, then a draft at `docs/prd/<ticket-id>-<slug>.md` with exact route contracts, data changes, UI copy, prompts, test plan, and build order, reviewed until the user approves it. Use when a ticket's Details names a PRD path or the user asks for a PRD. Not for bug fixes, small improvements, tooling, or docs tickets."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# PRD Creator

Writes stage 1b of the workflow in `CLAUDE.md`: the exact implementation spec
that sits between a big story and its code. The ticket says *what* and
*why*. The PRD says *exactly how*.

## Trigger Gate

Proceed only when one of these holds:

- The ticket's Details carries a `PRD: docs/prd/<ticket-id>-<slug>.md`
  bullet, meaning `ticket-system` made the PRD call "required".
- The user asks for a PRD.

Do not trigger for bug fixes, small improvements, tooling, or docs tickets.
Those go straight to code. A ticket that says `No PRD — <reason>.` gets no
PRD unless the user overrides it, and then the bullet is refined first. If
there is no ticket yet, write one with `ticket-system` first.

## Ticket and PRD Split

- The ticket owns the behavior, scope, and settled decisions. The PRD links
  to the ticket and never restates or reopens them.
- A new question found while writing goes into the ticket's
  `## Open Questions`, phrased as a question. The generator gate then blocks
  `in_progress` until the user clears it. Never answer it on the user's
  behalf, and never settle it silently in the PRD.
- Write only `docs/prd/`, plus new entries in the ticket's
  `## Open Questions`. Module docs, `data-model.md`, code, and tests are
  read-only here.

## Read Order

1. The story, then its epic (Settled Decisions, Findings, roadmap order).
2. The owning `docs/modules/<module>/index.md` when it exists. It is current
   truth for Before.
3. `docs/modules/db/data-model.md`.
4. The code the story touches: `routes/`, `services/`, `db/models.py`,
   `templates/`, `static/js/`, prompts, `scripts/`, and the matching `tests/`.

## Steps

Each step ends with a pause. Do not merge steps, and do not start the next
until the user answers.

### 1. Gap analysis

Reply in chat (no file yet) with:

- **Affected:** each route, service, collection, template, prompt, script, and
  test file, with `file:line` and what changes there.
- **Conflicts:** places where the ticket contradicts the code or a module
  doc, or where two settled decisions collide.
- **Missing:** edge cases, error paths, and contract details the ticket does
  not settle.

Sort each gap by what it touches:

- **How** (a library, an index shape, a redirect detail, a rollout step):
  propose the answer the PRD will use and why. The user confirms it at the
  pause.
- **What or why** (scope, a behavior choice, a data effect the ticket did not
  settle): add it to the ticket's `## Open Questions` and say so. Do not
  propose an answer in the PRD.

**Pause:** ask the user to confirm the proposals, with up to four batched
AskUserQuestion items, and to clear any Open Questions added.

### 2. Draft

Write `docs/prd/<ticket-id>-<slug>.md` from
[`templates/prd-template.md`](templates/prd-template.md), with
`status: draft`. Reuse the ticket's slug. Fill every section. A section that
does not apply reads `None — <reason>.`

- **Before** cites the module doc section or `file:line`. A new flow reads
  `None (new).`
- **Route contracts** are exact: method, path, auth guard, request fields,
  the response (status, redirect target, or JSON shape), and each error case.
- **Data changes** are listed, not decided. Each one is handed to the
  [`schema-check`](../schema-check/SKILL.md) skill at implementation, and the
  PRD says so. The PRD never writes `data-model.md`.
- **UI copy** quotes Chinese verbatim from `templates/` and `static/js/`.
  New copy is marked proposed.
- **Test plan** names `tests/test_<area>.py` per scenario, with OpenRouter and
  any other external call mocked.
- **Implementation order** is a numbered list in which each step leaves
  `pytest` green.

**Pause:** summarize the PRD in five lines or fewer, list any proposed copy
and assumptions, and ask for review.

### 3. Review

Revise in rounds. Keep the user's earlier decisions unless they reopen them.

Approval is the user's review, and it is the gate between a PRD and its code:

- The user reads the PRD and approves it in their own words. Ask in plain
  text and end the turn. Never put approval behind a multiple-choice prompt,
  and never approve on the user's behalf.
- On approval, set `status: approved`, `approved: YYYY-MM-DD`, and
  `reviewer:` to the user's name, then end the turn. Approval never starts
  code. Implementation begins only when the user asks for it.

A ticket that needs a PRD moves to `in_progress` only once its PRD is
`approved` and its Open Questions read `- None.`

## Lifecycle

- During implementation, the PRD joins the sync chain in `CLAUDE.md`. Code
  that diverges from it is a defect in both. Fix both in the same turn. A
  change to an approved contract goes back to the user first.
- After implementation, the [`prd-report`](../prd-report/SKILL.md) skill
  checks the PRD against the running app. The user's approval of that report
  closes the ticket.
- Once the ticket resolves, the PRD is a historical record and is not edited
  again. Its rules are folded into the owning module doc at doc sync, and the
  module doc stays current truth.

## Handoff

End each turn with the step you are on and what you are waiting for. After
approval, end with:

- The PRD path and the ticket it implements.
- Open Questions added to the ticket, if any.
- The data changes waiting on `schema-check`.
- A reminder that this skill writes the spec only. Implementation starts
  only when the user asks for it.
