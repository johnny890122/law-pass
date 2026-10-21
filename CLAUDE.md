# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Flask + MongoDB + OpenRouter quiz app for Taiwan law exams, deployed on
Heroku. The project intro is pending its own ticket. Until then,
[README.md](README.md) is the overview.

## Workflow

Ticket first. Every non-trivial change starts as an `LP-XXXX` ticket and lands
with its docs in sync.

| Stage | Home | Required |
| --- | --- | --- |
| 1. Ticket | [docs/issues/](docs/issues/): `LP-XXXX` | All but trivial changes |
| 1b. PRD | `docs/prd/<ticket-id>-<slug>.md` | Only when the ticket calls for one |
| 2. Artifact | `artifacts/LP-XXXX-<slug>/` | Only when a screen has a visual choice to make |
| 3. Code | `routes/` `services/` `db/` `templates/` `static/` `tests/` | Always |
| 4. Doc sync | `docs/modules/` and `docs/changelog/` | When behavior or a product rule changes |

Rules that make the flow hold:

- **No ticket, no code.** Before editing code, name the `LP-XXXX` you are
  working under. Trivial changes skip the ticket: typos, dependency bumps,
  lint fixes, and one-line obvious bugs. Anything touching behavior, data,
  prompts, or schema is not trivial. If unsure, ask.
- **Tickets come from the [`ticket-system`](.claude/skills/ticket-system/SKILL.md) skill.**
  The user writes the requirement. Claude grounds it in the code, drafts the
  ticket, and asks only about gaps that change its shape. Everything else goes
  under `## Open Questions`.
- **Open Questions are cleared before code.** A ticket moves to `in_progress`
  only when its `## Open Questions` reads `- None.`. The generator refuses
  otherwise. Never answer a question on the user's behalf.
- **A PRD is implemented only after the user has reviewed it.** Asked to
  implement a ticket whose PRD is not `approved`, stop before any code or
  status change. Give the PRD path, a summary of five lines or fewer, and its
  proposed copy and assumptions, then end the turn. Never ask for approval
  inline, as a step of the implement request. Approval is the user's own
  review, recorded as [`prd-creator`](.claude/skills/prd-creator/SKILL.md)
  describes, and it never starts code by itself. Implementation begins only
  when the user asks for it once the PRD is `approved`.
- **Schema changes run [`schema-check`](.claude/skills/schema-check/SKILL.md).**
  A field, index, collection, or `LAW_TYPES` key change goes through it
  before code lands. [docs/modules/db/data-model.md](docs/modules/db/data-model.md)
  is the schema's single source of truth, and `tests/test_schema_drift.py`
  fails when code and that doc disagree.
- **Status drives filing.** Change the `status` field and run
  `python3 .claude/skills/ticket-system/scripts/generate_issues_index.py`.
  Never move ticket files by hand.
- **Commits** go on `main`, and the message starts with `LP-XXXX: `. Trivial
  un-ticketed commits carry no prefix.
- **Keep the chain in sync.** Code that diverges from its ticket, PRD, or
  module doc is a defect in both. Fix both in the same turn, or say plainly which one you
  left behind. A ticket that turns out to be wrong gets refined, not silently
  overridden in code.

### Done gate

A ticket resolves only when all four hold:

1. **`pytest` green.** A behavior or data change adds or updates a test in
   `tests/`. OpenRouter is mocked, never called live.
2. **`flake8` clean**, using the repo's [.flake8](.flake8).
3. **Seen working in the app.** Run `python app.py` with a `.env` copied from
   [.env.example](.env.example) and a reachable MongoDB, then exercise the
   change in a browser using Playwright MCP. A template or CSS change is
   seen at phone 390x844, tablet 768x1024, and desktop 1440x900, and passes
   the check in [docs/modules/ui/index.md](docs/modules/ui/index.md). If the
   app cannot run, say so. Never claim it was seen.
4. **Docs synced.** Update the owning module doc and write a changelog entry,
   or have the ticket state why none applies.

A PRD-backed ticket also needs its report at
`docs/reports/<ticket-id>-<slug>/report.md` to be `approved` by the user.
The [`prd-report`](.claude/skills/prd-report/SKILL.md) skill writes it once
the four hold. This is checked by hand, like PRD approval.

Then check every acceptance box, or rewrite it with a note. Write a 2–3 line
`## Resolution` that links the changelog entry (and, for a PRD ticket, the
report), fill in `resolved:`, and run the generator.
`docs/issues/closure-debt.md` must gain no row.

### PRDs (conditional)

A big feature story needs an exact spec before code: route contracts, data
changes, UI copy, a test plan, and build order. Every story or feature ticket
makes the call in Details, as `PRD: docs/prd/<ticket-id>-<slug>.md` or
`No PRD — <reason>.` Bug fixes and small improvements rely on the ticket
alone.

Write them with the [`prd-creator`](.claude/skills/prd-creator/SKILL.md)
skill. The ticket owns *what* and *why*, and the PRD owns *exactly how*. A
PRD never reopens a settled decision. A new question goes into the ticket's
`## Open Questions`. The closing step is the
[`prd-report`](.claude/skills/prd-report/SKILL.md) skill: it checks the
running app against the PRD and writes a plain-language report with
screenshots, which the user signs off. Once the ticket resolves, the PRD and
its report are historical records, and the PRD's rules live on in the module
doc.

### Artifacts (conditional)

There is no designer, so when a ticket turns on what a screen should look like,
the user picks by looking. Every ticket makes the call either way. A ticket
without an artifact carries `No artifact — <reason>.` in Details.

The test is not "does this touch the frontend". It is **"is there a choice here
the user should make by looking?"**

Build them with the [`neta-design`](.claude/skills/neta-design/SKILL.md)
skill, which covers alignment, grounding, tokens, and verification. It also
builds the design-system directions, whose token values come from a
reference site captured with [`site-capture`](.claude/skills/site-capture/SKILL.md).
The contract below is what every artifact folder must satisfy.

- **Two or three** standalone `.html` variants in `artifacts/LP-XXXX-<slug>/`,
  with no build step and no Flask.
- Screenshot each variant with Playwright MCP at **phone 390x844**, **tablet
  768x1024**, and **desktop 1440x900** into `shots/<variant>-<viewport>.png`,
  where `<viewport>` is `phone`, `tablet`, or `desktop`. The app is
  mobile-first, so the phone shot is the primary one.
- Record the pick in `DECISION.md`: the winner and why, what was rejected, what
  the real implementation must keep, and **who decided and on what evidence**.
- Nothing in `artifacts/` ships verbatim. The winner is rebuilt in `templates/`
  against real data, and the decision is folded into the module doc.

### Docs

One doc tree, with no promotion layer. Both kinds of doc record decisions
rather than restating code.

```
docs/
├── issues/                     # tickets, generator-managed
├── prd/
│   └── <ticket-id>-<slug>.md   # implementation spec, when a ticket calls for one
├── reports/
│   └── <ticket-id>-<slug>/     # audit report of an implemented PRD, with shots/
├── references/
│   └── <site-slug>/            # external reference site: spec.md, tokens.md, shots/
├── modules/
│   ├── index.md                # owner map: module → what it owns
│   ├── <module>/index.md       # current truth for one area
│   └── db/data-model.md        # db's module doc: the schema's source of truth
└── changelog/
    ├── index.md                # file → LP ids + one line
    └── YYYY-MM-DD-<slug>.md    # one entry per landing
```

- **Module docs** describe current behavior. Product rules come first: what
  the quiz, inventory, grading, or auth must do, and why. A short `## Code`
  section follows, naming the files that own it. Create a module doc the first
  time a ticket changes that area, and update `modules/index.md` in the same
  change.
- **Changelog entries** are the product iteration log. Write one per landing,
  and one entry may cover several LP ids. Include a Was / Now table for
  behavior changes and a "Deliberately not done" list. Add a row to
  `changelog/index.md`. The ticket's Resolution links here instead of repeating
  it.
- **Reference captures** in `docs/references/<site-slug>/` are written by the
  [`site-capture`](.claude/skills/site-capture/SKILL.md) skill. Each is a
  dated, descriptive record of an external site that `neta-design` derives
  tokens from. It is never a record of law_pass. Re-capture a reference
  rather than patching it.
- When a folder has an `index.md`, read it first and update it in the same
  change.
- `docs/requirements.md`, `docs/design.md`, and `docs/tasks.md` are a retired
  SDD flow, pending removal under a ticket. Read them for context only. Never
  update them, and never treat them as current truth.

## Conventions

- English for tickets, docs, and changelog. Quote Chinese UI copy and law text
  verbatim.
