---
name: ticket-system
description: "Create, refine, select, or resolve tracked issues (`LP-XXXX`) in `docs/issues/`. Use when the user asks to add/write/refine a ticket, choose what to work on, or close one out. Ticket writing only: ground the user's requirement in the code, ask only about real gaps, write the ticket, and name the docs it will sync. Never implement."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Ticket System

Turns the user's requirement into a short, actionable ticket under
`docs/issues/`. This skill writes stage 1 of the workflow in `CLAUDE.md` and
nothing else.

## Guardrails

- Do not implement. Write only under `docs/issues/`. Never edit code,
  `tests/`, `docs/modules/`, or `docs/changelog/` from this skill.
- Read before writing: `CLAUDE.md`, `docs/issues/README.md`,
  `docs/issues/pending.md`, `assets/TICKET_TEMPLATE.md`, the owning
  `docs/modules/<module>/index.md` when it exists, and any referenced ticket.
- The legacy `docs/requirements.md`, `docs/design.md`, and `docs/tasks.md` are
  being retired. Read them for context; never cite them as current truth.
- Keep tickets short enough to skim. Concrete bullets, verifiable checks.

## Modes

1. Create a new ticket.
2. Refine an existing `LP-XXXX`.
3. Help choose the next pending ticket: list `docs/issues/pending.md` by
   priority and area, then ask which to inspect.
4. Resolve a ticket (see Resolving Tickets).

## Authoring: Draft From the Brief

The user writes requirements directly. Do not interview them by default.

1. Read the inventory, the template, and the owning module doc.
2. Ground the requirement in the code: `rg` through `routes/`, `services/`,
   `db/models.py`, `templates/`, and `tests/` for what exists today.
3. Ask with AskUserQuestion **only** about gaps that change the ticket's shape:
   scope, a behavior choice, a data effect. Batch up to three, and offer a
   "Leave as Open Question" option. Everything else goes to `## Open Questions`.
4. Pick the id: the **highest `LP-` id across every status folder**, plus one.
   A story takes its epic id plus the next two-digit sequence (`LP-0012-03`).
5. Write the ticket from the template. New tickets are `status: pending` in
   `docs/issues/pending/`; stories go in `docs/issues/pending/<epic-file-stem>/`.
6. Run the generator:

```bash
python3 .claude/skills/ticket-system/scripts/generate_issues_index.py
```

## Open Questions Gate

Open Questions must be cleared before implementation starts. The generator
refuses an `in_progress` or `resolved` ticket whose `## Open Questions` holds
anything other than `- None.`

Clear a question one of two ways:

- **Answered** — move the answer into `## Details` or
  `### Settled Decisions`, then delete the question.
- **Deferred** — move it to `### Deferred Decisions` or a new ticket, naming
  which.

Never answer a question on the user's behalf. A blocked ticket closes as
`wont_fix` with its questions intact (see Blocked Work).

## Artifact Call

Stage 2 (artifacts) is conditional, and the ticket makes the call either way.

- **Required** when the ticket turns on what a screen should look like: a
  choice the user should make by looking. There is no designer, so the
  variants are how the user decides.
- **Skipped** otherwise: routes, services, data, prompts, tests, bug fixes,
  and pages that follow an existing template.

A skipped ticket carries one Details bullet: `No artifact — <reason>.`

An artifact-backed ticket:

- Names the visual question in Details, the two or three variants worth
  building, and what distinguishes them. Variants must differ on the question.
- Records which visual decisions are **not** open. Every variant must respect
  those.
- Adds an Acceptance Criteria box:
  `Variants in artifacts/LP-XXXX-<slug>/ screenshot at phone (390x844) and desktop (1440x900), reviewed with the user; choice recorded in DECISION.md.`
- Lists `artifacts/LP-XXXX-<slug>/` in Related Files.
- Implements the picked variant in `templates/` in the same ticket when the
  change is small, or as a follow-up story otherwise.

## Test Coverage

Any ticket that changes user-visible behavior or stored data plans its test in
the same delivery.

- Name the target module (`tests/test_<area>.py`) in the `pytest`
  Acceptance Criteria box.
- Sketch the scenario in the Handoff Appendix when it is not obvious: setup,
  action, the expected response or collection change.
- Calls to OpenRouter are mocked in tests, never live.
- A template-only or copy-only change is exempt. Say so in the box rather than
  deleting it.

## Doc Sync Targets

Name which docs the ticket will touch when it lands, per `CLAUDE.md` Docs:

- The owning `docs/modules/<module>/index.md`. Name it even if it does not
  exist yet, because the implementer creates it.
- A changelog entry under `docs/changelog/`.
- A bug fix that changes no rule syncs nothing. Rewrite the box as
  `Docs synced: none — <reason>.`

## Ticket Content

Follow `assets/TICKET_TEMPLATE.md` exactly.

- Frontmatter: `id`, `title`, `type`, `status: pending`, `priority`,
  `created`, blank `resolved`, `area`, optional `tags`, and `parent` for
  stories only.
- Area slugs follow the code: `quiz`, `question-gen`, `grading`, `laws`,
  `progress`, `inventory`, `i18n`, `auth`, `admin`, `ui`, `db`, `scripts`,
  `deploy`, `docs`, `tests`.
- `## Description`: 1–2 sentences on who needs what, and why now.
- `## Details`: current → desired behavior, scope, the artifact call, and out
  of scope.
- `## Acceptance Criteria`: checkboxes only, including the four done-gate boxes
  from `CLAUDE.md`.
- `## Open Questions`: unresolved human decisions, or `- None.`
- `## Related Files`: likely paths, backticked.
- `## Handoff Appendix`: optional. Use it when the discussion holds concrete
  decisions, edge cases, prompts, or test scenarios that a summary would lose.
  Rewrite them as handoff notes, not a transcript. Unresolved items never go
  here.

Skip `## Resolution` until the ticket resolves.

## Epics and Stories

Use an epic when several tickets share one goal and one done condition.

- Epic: `type: epic`, a normal `LP-XXXX` id. Details lists the planned stories
  as a roadmap. Acceptance Criteria include "all child stories closed".
- Story: `type: story`, `parent: LP-XXXX`, id `LP-XXXX-YY`, kebab-case
  filename, filed in a folder named exactly after the epic file's stem.
- Create stories only when their scope is settled. Until then they stay as
  roadmap bullets.
- Resolve the epic only after every story is `resolved` or `wont_fix`.

## Filing by Status

The generator validates the store, files tickets by status, and rewrites
`README.md`, `in-progress.md`, `pending.md`, `done.md`, and `closure-debt.md`.
Run it after every ticket edit. Never move ticket files by hand.

- Statuses: `pending`, `in_progress`, `resolved`, `wont_fix`.
- It hard-fails on duplicate or malformed ids, stories that do not extend their
  parent, unknown statuses, completed epics with active stories, uncleared Open
  Questions on `in_progress` or `resolved`, and filing collisions.
- Ticket images go in `<ticket-folder>/img/<lowercase-id>/` and move with the
  ticket.

### Blocked Work

There is no `blocked` status. Work that cannot proceed closes as `wont_fix` with
a `blocked` tag, and its `## Resolution`:

1. Opens with **blocked, not abandoned** and names the blocker.
2. States the condition for reopening.
3. Rewrites the Acceptance Criteria with notes, never silently ticked.

Do not leave blocked work `pending`. A pending story keeps its epic from ever
resolving.

## Refining Tickets

- Preserve `id`, `created`, and the filename. A title change updates the
  frontmatter and `# Heading` only.
- Ask about existing Open Questions before rewriting them. Keep the uncertainty
  unless the user answers it.
- Rerun the generator if frontmatter changed.

## Resolving Tickets

A ticket moves to `resolved` only when the done gate in `CLAUDE.md` holds:

1. Every Acceptance Criteria box is checked, or rewritten with a note saying
   why it no longer applies. Never leave a box silently unchecked.
2. `## Resolution` has 2–3 lines: what landed, what was deliberately not done,
   and a link to the changelog entry that tells the full story.
3. `resolved: YYYY-MM-DD` is filled.
4. The generator runs, and `closure-debt.md` gains no row.

## Handoff

End with:

- The ticket's id, title, and path.
- Remaining Open Questions, and the reminder that they block `in_progress`.
- The artifact call (required or skipped, and why).
- The doc sync targets.
- A reminder that this skill writes tickets only, and implementation happens
  separately.
