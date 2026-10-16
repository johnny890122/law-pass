# 2026-10-16 — prd-report skill

**LP ids:** LP-0001-04

A PRD-backed ticket now closes on an audit report the user signs off. The new
[`prd-report`](../../.claude/skills/prd-report/SKILL.md) skill walks the real
running app against the approved PRD. It writes
`docs/reports/<ticket-id>-<slug>/report.md` from one template, with phone
screenshots of the happy path and each edge case. The report is in plain
language for an auditor who does not read code. No product behavior changed,
so no module doc applies.

| Area | Was | Now |
| --- | --- | --- |
| Done gate, PRD tickets | The four boxes. "Seen working" was a Playwright session that left no record. | Also, the report at `docs/reports/<ticket-id>-<slug>/report.md` must read `status: approved`, with `approved:` and `reviewer:` filled. This is checked by hand, like PRD approval. |
| Ticket `## Resolution` | Links the changelog entry. | A PRD ticket also links its report (`ticket-system` Resolving Tickets). |
| Ticket template | Five Acceptance Criteria boxes. | A sixth box: `PRD tickets only: report at docs/reports/LP-XXXX-<slug>/report.md is approved.` A skipped PRD call deletes it (`ticket-system` PRD Call). |
| PRD lifecycle | Approved, then a historical record once the ticket resolves. | `prd-report` checks it against the running app first. The report becomes a historical record with it (`prd-creator` Lifecycle). |
| Deviations | Code that diverged from a PRD was a defect in both, caught only by reading. | The report lists each deviation. A report with any deviation is not offered for sign-off until the code or the PRD is fixed. |

Smoke run against a throwaway stand-in PRD for the existing login → quiz flow,
on a dedicated local database. It produced five happy-path phone shots, two
browser edge cases (「用戶名稱不存在，請聯繫管理員」 and the 「題目數量不足」
dialog), and a sign-off pause. Two findings came out of it:

- **No test covers a grading failure.** The stand-in PRD's "test only" row
  had no evidence, so it failed and blocked sign-off, as the skill requires.
  A throwaway test cleared it for the run. The real coverage gap in
  `routes/quiz.py` (the 503 on a short-answer grading failure) remains.
- **The app has no site icon.** The first page load logs a `/favicon.ico`
  404, so every report's clean-console check trips on it until that is
  fixed.

The smoke output, the stand-in PRD, and the throwaway test were deleted, not
committed.

## Deliberately not done

- Reports for tickets without a PRD.
- Generator enforcement of the report gate (LP-0001-04 Deferred Decisions).
- A `docs/reports/` index. Each ticket's Resolution links its own report.
- PDF export, or publishing a report outside the repo.
- Git LFS for report screenshots (LP-0001-04 Deferred Decisions).
- A report for `LP-0002-01` or any other real ticket.
