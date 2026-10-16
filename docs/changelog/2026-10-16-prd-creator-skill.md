# 2026-10-16 — prd-creator skill

**LP ids:** LP-0001-03

Big feature stories now get an exact implementation spec before code. The new
[`prd-creator`](../../.claude/skills/prd-creator/SKILL.md) skill is a lean
port of moblab's `prd-creator` (Workflow A only). It runs a gap analysis
against the code, drafts `docs/prd/<ticket-id>-<slug>.md` from one template,
and revises it until the user approves. No product behavior changed, so no
module doc applies.

| Area | Was | Now |
| --- | --- | --- |
| Workflow stages | Ticket → Artifact → Code → Doc sync. Big stories packed contracts into Details and the Handoff Appendix. | A conditional stage 1b, PRD, sits between Ticket and Artifact. Existing stage numbers are unchanged. |
| `in_progress` gate | Open Questions read `- None.` | Also, a ticket that calls for a PRD waits for that PRD's `status: approved`. This is checked by hand, not by the generator. |
| Ticket Details | Artifact call only. | Every story and feature also carries `PRD: docs/prd/…` or `No PRD — <reason>.` (`ticket-system` PRD Call section and the ticket template). |
| Sync chain | Code ↔ ticket ↔ module doc. | The PRD joins the chain while its ticket is open, and becomes a historical record once the ticket resolves. Its rules fold into the module doc. |
| Gap handling | — | "How" gaps get a proposal the user confirms at the step 1 pause. "What or why" gaps go to the ticket's Open Questions, never into the PRD. |

Smoke run on `LP-0002-01`: the gap analysis found three conflicts. A plain
unique `users.email` index would fail boot on users without an email. Heroku
would build an `http://` redirect URI without `ProxyFix`. Username-created
sessions would outlive the cutover. Answering them, the user reversed a
settled decision: existing users are now deleted with their progress, not
backfilled. The ticket was refined first, and the draft PRD followed.

## Deliberately not done

- Workflow B (handbook update). Stage 4 doc sync covers it.
- Handbook onboarding, `product-line-profile.yaml`, variations, the
  comparison/merged template pair, `context.md` sessions, the BE/FE ticket
  split, Jira links, metrics, and the `[Status: …]` footer.
- Generator enforcement of PRD approval (LP-0001-03 Deferred Decisions).
- A `docs/prd/` index. Each ticket links its own PRD.
- PRDs for the other `LP-0002` stories. Each gets its PRD call when refined.
