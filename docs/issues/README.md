# Issues

Stage 1 of the ticket-first workflow in [CLAUDE.md](../../CLAUDE.md):
every non-trivial change starts as a ticket here.

> Generated from ticket frontmatter by `.claude/skills/ticket-system/scripts/generate_issues_index.py`. Do not edit by hand.
> Run `python3 .claude/skills/ticket-system/scripts/generate_issues_index.py` from the repo root to refresh after editing ticket frontmatter.

## Status Overviews

- [In Progress](./in-progress.md) — 2
- [Pending](./pending.md) — 8
- [Done](./done.md) — 11 (resolved 11, won't-fix 0)
- [Closure Debt](./closure-debt.md) — 0 completed ticket(s) not fully closed

## Folder Layout

- Every ticket is filed under the folder matching its canonical status: `pending/`, `in_progress/`, `resolved/`, or `wont_fix/`.
- Standalone tickets and epic files live directly in their status folder. Stories live in `<status>/<epic-folder>/`.
- A story is filed by its own status, independently of its parent epic. Mixed-status epics therefore have matching epic folders under more than one status.
- Ticket-specific images live at `<ticket-parent>/img/<lowercase-ticket-id>/` so the generator can move them with the ticket.
- The filing is automated: change the `status` field, rerun the generator, and it moves the file. Never move ticket files by hand.

## Ticket Metadata

Tickets are Markdown files with YAML frontmatter. Filenames are stable and do not change when status changes; use the `status` field instead.

| Field | Values / Format | Notes |
| --- | --- | --- |
| `id` | `LP-0001` | Stable ticket identifier. Take the highest id across every status folder and increment. The generator fails on duplicates. |
| `title` | Text | Human-readable ticket title. |
| `type` | `bug`, `feature`, `improvement`, `refactor`, `todo`, `epic`, `story` | Work category. Epics group story tickets. |
| `status` | `pending`, `in_progress`, `resolved`, `wont_fix` | Drives the overviews and which folder the ticket is filed in. |
| `priority` | `high`, `medium`, `low` | Used for sorting within status. |
| `created` | `YYYY-MM-DD` | Creation date. |
| `resolved` | `YYYY-MM-DD` or blank | Fill when resolved. |
| `area` | Short slug | Example: `quiz`, `question-gen`, `grading`, `laws`, `auth`, `ui`, `db`, `docs`. |
| `parent` | `LP-XXXX` or blank | Stories only: id of the parent epic. Story ids extend the epic id (`LP-XXXX-01`), and story files live in a folder named after the epic file. |
| `tags` | YAML list | Optional discovery labels. |

Use `.claude/skills/ticket-system/assets/TICKET_TEMPLATE.md` when creating a new ticket.
