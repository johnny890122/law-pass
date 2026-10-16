---
id: LP-0001-04
title: PRD-report skill as the closing gate of PRD tickets
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
  - audit
---

# PRD-report skill as the closing gate of PRD tickets

## Description

A PRD says exactly how a big story will be built, but nothing shows an auditor
what was actually built and that it works. A `prd-report` skill writes a
plain-language report of an implemented PRD, with screenshots of the full user
journey. The user's sign-off on that report is the closing gate of every
PRD-backed ticket.

## Details

- Current: the done gate's "Seen working" step is a Playwright session that
  leaves no record. Nothing checks the running app against the PRD's route
  contracts, edge cases, or data changes, and once the ticket resolves the
  PRD is only a historical record. No PRD has been implemented yet. The first
  will be `LP-0002-01`, whose PRD is still `draft`.
- Desired: `.claude/skills/prd-report/SKILL.md` plus one
  `templates/report-template.md`. The skill name pairs with `prd-creator`.
  - **Trigger gate:** the ticket has an `approved` PRD, its code is done, and
    `pytest` and `flake8` pass. Or the user asks for a report. It does not
    trigger for tickets without a PRD.
  - **Read order:** the ticket, then its PRD (Before → After, Route
    Contracts, Data Changes, Business Rules and Edge Cases, Test Plan), then
    the `docs/modules/db/data-model.md` Change Log rows for the ticket's LP
    id, then the ticket's code diff and tests.
  - **Output:** `docs/reports/<ticket-id>-<slug>/report.md`, reusing the
    PRD's slug, with screenshots in `shots/` beside it. Both are committed.
  - **Report sections**, in order:
    1. **Header:** links to the ticket, PRD, and changelog entry; the commit
       it was verified at; the environment (local app, DB name, test account,
       and any seed data the journey needs); who prepared it and when; and
       `status`, `approved`, and `reviewer`.
    2. **Summary:** three to five plain sentences on what changed for the
       user.
    3. **User journey (happy path):** one numbered step per user action, each
       with a phone screenshot and a one-line caption of what the user does
       and sees. Chinese UI copy is quoted verbatim.
    4. **Edge cases:** one row per row of the PRD's Business Rules and Edge
       Cases table: the scenario, what the user sees, the evidence, and pass
       or fail. The evidence is a screenshot when the case can be reached in
       the browser. Otherwise it is the covering test
       (`tests/test_<area>.py::test_name`), marked "test only".
    5. **API changes:** one row per route in the PRD's Route Contracts: method
       and path, who can call it, what it does in plain words, and whether it
       is new, changed, or removed. `None.` when no route changed.
    6. **Database changes:** one row per collection change, in plain words:
       what changed, what happened to existing data, the migration, and where
       it ran. Taken from the `data-model.md` Change Log, not from the PRD,
       because a Change Log row is the confirmed record. `None.` when nothing
       changed.
    7. **Deviations from the PRD:** each place where the running app differs
       from the PRD, or `None.`
    8. **How it was verified:** the `pytest` and `flake8` results, and how the
       app was run.
  - **Human-friendly rules:** the reader is an auditor who does not read
    code. Plain English. No code blocks, stack traces, or JSON dumps.
    Technical names (routes, collections, fields) appear only in the API and
    database tables, and each table has a plain-words column.
  - **Screenshots:** taken with Playwright MCP from the real running app
    (`python app.py`, local MongoDB, a test account made with
    `scripts/add_user.py`), never from a mock. Phone 390x844 for every step.
    Desktop 1440x900 only for a screen whose layout differs at desktop. The
    console must be clean, as in `design-variants` Verify. Name shots
    `shots/NN-<step>-phone.png` (or `-desktop.png`), and look at each saved
    PNG before using it. No production data and no real personal data on
    screen.
  - **Deviations block sign-off:** under the `CLAUDE.md` sync chain, a
    deviation is a defect in both the code and the PRD. Fix the code, or
    refine the PRD (a change to an approved contract goes back to the user
    first), then re-run the affected steps. A report whose Deviations section
    lists anything is not offered for sign-off.
  - **Sign-off:** the report starts `status: draft`. The user reviews it in
    rounds, and every screenshot a revision affects is re-shot. When the user
    approves, set `status: approved`, `approved: YYYY-MM-DD`, and
    `reviewer:`. Never approve on the user's behalf.
  - **Lifecycle:** once its ticket resolves, the report is a historical
    record, like the PRD, and is not edited again.
- **Closing gate wiring:** a PRD-backed ticket resolves only when its report
  is `approved`. This is checked by hand, like PRD approval.
  - `CLAUDE.md`: the Done gate states the rule for PRD-backed tickets, the
    PRDs section names the report as the closing step, and the Docs tree
    gains `reports/`.
  - `ticket-system`: Resolving Tickets checks for the approved report, and a
    PRD ticket's `## Resolution` links it next to the changelog entry. The
    PRD Call adds the report box to a ticket whose PRD is required.
  - `assets/TICKET_TEMPLATE.md`: carries the box
    `PRD tickets only: report at docs/reports/LP-XXXX-<slug>/report.md is approved.`
  - `prd-creator` Lifecycle: after implementation, `prd-report` checks the
    PRD against the running app.
- No artifact. The report is a Markdown document, not an app screen, so
  there is no visual choice to make by looking.
- No PRD — tooling.
- Out of scope:
  - Reports for tickets without a PRD.
  - Having the generator enforce the report gate.
  - A `docs/reports/` index, because each ticket's Resolution links its own
    report.
  - PDF export, or publishing the report outside the repo.
  - Writing a report for `LP-0002-01` or any other real ticket.

## Acceptance Criteria

- [x] `.claude/skills/prd-report/SKILL.md` and `templates/report-template.md`
      cover the trigger gate, read order, the eight report sections, the
      human-friendly rules, the screenshot rules, the deviation rule,
      sign-off, and lifecycle above.
- [x] `CLAUDE.md` makes the approved report the closing gate of a PRD-backed
      ticket and shows `docs/reports/` in the Docs tree. `ticket-system`
      (Resolving Tickets and PRD Call), the ticket template, and
      `prd-creator` Lifecycle all point to the skill.
- [x] `pytest` green: no code or test change. The box stays to confirm
      nothing regressed. 27 passed.
- [x] `flake8` clean.
- [x] Seen working: no PRD is implemented yet, so the smoke run follows the
      skill against a throwaway stand-in PRD for the existing login → quiz
      flow. It produces a draft report with phone screenshots of the happy
      path, two browser edge cases (an unknown username shows
      「用戶名稱不存在，請聯繫管理員」, and too few questions shows
      「題目數量不足，請聯繫管理員生成更多題目。」), one "test only" edge case
      (a grading failure), and a sign-off pause. The smoke output is
      deleted, not committed. Note: no existing test covers a grading
      failure, so that row first failed and blocked sign-off, as the
      deviation rule requires. A throwaway test, deleted with the smoke
      output, cleared it. The first page load also logged a `/favicon.ico`
      404 that predates this work. Both are recorded in the changelog entry.
- [x] Docs synced: `CLAUDE.md`, `ticket-system`, `prd-creator`, and a
      changelog entry. No module doc applies, because no product behavior
      changes.

## Open Questions

- None.

## Related Files

- `.claude/skills/prd-report/` (new)
- `.claude/skills/prd-creator/SKILL.md`
- `.claude/skills/prd-creator/templates/prd-template.md`
- `.claude/skills/design-variants/SKILL.md`
- `.claude/skills/ticket-system/SKILL.md`
- `.claude/skills/ticket-system/assets/TICKET_TEMPLATE.md`
- `CLAUDE.md`
- `docs/modules/db/data-model.md`
- `docs/reports/` (new)
- `scripts/add_user.py`
- `routes/auth.py`
- `routes/quiz.py`

## Handoff Appendix

### Settled Decisions

- The approved report is the closing gate of a PRD-backed ticket. The user
  chose this on 2026-10-16.
- The report is Markdown at `docs/reports/<ticket-id>-<slug>/report.md`, with
  `shots/` beside it, committed. The user chose this on 2026-10-16.
- The user signs off: the report goes from `draft` to `approved`, with the
  reviewer and the date recorded. The user chose this on 2026-10-16.
- The report is for audit only and must be human friendly. Its reader does
  not read code. This is from the user's brief.

### Behavior Details

- A Change Log row whose `Ran` cell reads `pending: heroku` appears in the
  Database changes table as "not yet run on production". Under the
  `data-model.md` rule, that ticket cannot resolve anyway until the cell is
  filled.
- An edge case that needs a live OpenRouter failure, or any other state that
  cannot safely be reached in the running app, is shown by its test, marked
  "test only", and never staged against a live service.

### Deferred Decisions

- Screenshot size in git. A report with 20 phone PNGs adds a few MB to the
  repo. Move `docs/reports/**/shots/` to Git LFS if repo size starts to
  matter.
- Generator enforcement of the report gate, parallel to the deferred PRD
  approval check in `LP-0001-03`. File it if the manual gate gets skipped in
  practice.

## Resolution

Landed the `prd-report` skill and its template, the report gate in the
`CLAUDE.md` Done gate, and the pointers in `ticket-system`, the ticket
template, and `prd-creator`. Deliberately not done: generator enforcement and
a `docs/reports/` index. The smoke run found two gaps it did not fix: no test
covers a grading failure, and the app has no favicon. Full story in
[2026-10-16-prd-report-skill](../../../changelog/2026-10-16-prd-report-skill.md).
