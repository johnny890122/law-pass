---
name: prd-report
description: "Write the plain-language audit report that closes a PRD-backed `LP-XXXX` ticket: walk the real running app against its approved PRD, screenshot the user journey and edge cases at phone size, and record the user's sign-off in `docs/reports/<ticket-id>-<slug>/report.md`. Use when a ticket with an approved PRD has its code done and `pytest` and `flake8` pass, or the user asks for a report. Not for tickets without a PRD."
---

# PRD Report

Closes the PRD chain in `CLAUDE.md`. The PRD says exactly how a story will be
built. The report shows an auditor what was built and that it works, in
plain language, with screenshots of the real app. The user's sign-off on the
report is the closing gate of every PRD-backed ticket.

## Trigger Gate

Proceed only when one of these holds:

- The ticket's PRD is `status: approved`, its code is done, and `pytest` and
  `flake8` pass.
- The user asks for a report.

Do not trigger for a ticket without a PRD. A ticket that says
`No PRD — <reason>.` closes on the done gate alone. If `pytest` or `flake8`
fails, fix that first. A report never records a red run.

## Read Order

1. The ticket: Acceptance Criteria, Settled Decisions, and Behavior Details.
2. Its PRD: Before → After, Route Contracts, Data Changes, Business Rules and
   Edge Cases, and Test Plan.
3. The `## Change Log` rows in `docs/modules/db/data-model.md` whose `LP`
   cell is the ticket's id.
4. The ticket's code diff (its `LP-XXXX: ` commits, plus the working tree if
   the code is not committed yet) and the tests it added or changed.

## Writing for the Auditor

The reader is an auditor who does not read code.

- Plain English. No code blocks, stack traces, or JSON dumps.
- Technical names (routes, collections, fields) appear only in the API and
  database tables, and each of those tables has a plain-words column.
- Quote Chinese UI copy verbatim, as the screen shows it: 「題目數量不足」.
- Describe what the user does and sees, not how the code does it.

## Steps

Each step finishes before the next starts. The only pauses are a deviation
that needs the user (step 4) and sign-off (step 5).

### 1. Set up

- Run the real app with `python app.py`, using a `.env` copied from
  `.env.example`. Point `MONGO_URI` at a local MongoDB and a database made
  for the report, such as `mongodb://localhost:27017/lp_report_<id>`. Check
  the host is `localhost` before starting. Never use production data.
- Make a test account with `python scripts/add_user.py <name> "<display>"`.
  Use a made-up name. No real personal data appears on screen.
- Seed only the data the journey needs, and mark it as stand-in in the
  Header. Never copy it from production.
- Record the commit with `git rev-parse --short HEAD`, adding
  `+ working tree` when the ticket's code is not committed yet.

### 2. Walk the journey

Drive the app with Playwright MCP from the real running app, never from a
mock. Screenshots live in `docs/reports/<ticket-id>-<slug>/shots/`.

For each step of the PRD's happy path, one step per user action:

1. `browser_resize` to 390x844, then act as the user would.
2. `browser_console_messages` must show no errors, as in the
   `design-variants` Verify step. Fix the cause. Do not hide it.
3. `browser_take_screenshot` to `shots/NN-<step>-phone.png`, numbered in
   journey order. Then read the saved PNG and look at it. Re-shoot anything
   wrong before using it.
4. Add a 1440x900 shot, `shots/NN-<step>-desktop.png`, only when that
   screen's layout differs at desktop.

For each row of the PRD's Business Rules and Edge Cases table:

- **Reachable in the browser:** stage it locally, then screenshot it the
  same way.
- **Not safely reachable** (a live OpenRouter failure, a timeout, a race):
  run the covering test from the PRD's Test Plan on its own, as
  `pytest tests/test_<area>.py::test_name`. A pass is the evidence, marked
  "test only". Never stage the failure against a live service.
- **Neither:** the row fails. A case with no screenshot and no passing test
  is a deviation.

For each route in the PRD's Route Contracts, confirm it exists with the
stated auth guard, and that the journey or a test exercised it.

### 3. Draft

Write `docs/reports/<ticket-id>-<slug>/report.md` from
[`templates/report-template.md`](templates/report-template.md), with
`status: draft`. Reuse the PRD's slug. Fill every section in order. A section
with nothing to say reads `None.`

- **Edge cases:** one row per PRD Business Rules and Edge Cases row, with
  its id.
- **API changes:** one row per route in the PRD's Route Contracts, marked
  new, changed, or removed.
- **Database changes:** taken from the `data-model.md` Change Log rows, not
  from the PRD, because a Change Log row is the confirmed record. A `Ran`
  cell that reads `pending: heroku` becomes "not yet run on production".
  The ticket cannot resolve until that cell is filled anyway.
- **Header:** link the changelog entry once doc sync has written it. The
  report is not offered for sign-off without it.

### 4. Deviations

A deviation is any place where the running app differs from the PRD. Under
the `CLAUDE.md` sync chain it is a defect in both the code and the PRD.

- Fix the code, or refine the PRD. A change to an approved contract goes
  back to the user first. That is a pause.
- Re-run the affected steps, and re-shoot every screenshot they touch.
- A report whose Deviations section lists anything is not offered for
  sign-off.

### 5. Sign-off

**Pause:** offer the report for sign-off. Send the report path, a summary in
five lines or fewer, and the shot paths in journey order. Ask a specific
question, such as whether a caption matches what the auditor expects, rather
than "any feedback?".

Revise in rounds. Re-shoot every screenshot a revision affects, so the shots
always match the app. When the user approves, set `status: approved`,
`approved: YYYY-MM-DD`, and `reviewer:` to the user's name. Never approve on
the user's behalf.

## Lifecycle

- The report and its `shots/` are committed with the ticket.
- The ticket's `## Resolution` links the report next to the changelog entry.
- Once the ticket resolves, the report is a historical record, like the PRD,
  and is not edited again.

## Handoff

End each turn with the step you are on and what you are waiting for. After
approval, end with:

- The report path, and the ticket and PRD it covers.
- A reminder that the ticket now resolves through `ticket-system`, with the
  report linked in its `## Resolution`.
