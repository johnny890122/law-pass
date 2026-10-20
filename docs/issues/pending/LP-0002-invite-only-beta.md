---
id: LP-0002
title: Beta user stories
type: epic
status: pending
priority: high
created: 2026-10-16
resolved:
area: auth
tags:
  - user-stories
  - beta
---

# Beta user stories

## Description

The MVP serves a few hand-added users, but it trusts any typed username, has no
admin role, and gives learners no way to reach the admin. This epic records the
product's user stories for a beta with self-signup: Google sign-in, per-learner
law setup, admin-controlled generation, and a feedback line to the admin.

## Details

- Phase rules:
  - **Self-signup.** Any Google account with a verified email creates its
    own account on first sign-in. There is no console account creation:
    every account comes from self-signup, and admin edits happen in Atlas.
    This replaced invite-only on 2026-10-16.
  - **Admin-only generation.** Only the admin triggers question generation,
    using the platform OpenRouter key. Learners bringing their own key comes in
    a later phase, and nothing built now may block it.
- User stories, in roadmap form:

| As a… | I want… | So that… | Ticket |
| --- | --- | --- | --- |
| learner | to sign up and sign in with my Google account | I can join without an invite or an extra password | `LP-0002-01` |
| learner, on first login | to change my random display name and pick the laws I am studying | the app shows the name I want, and starts on my exam's laws, not 專利法 by default | `LP-0002-02` |
| admin | to be the only one who can generate questions or call admin endpoints | LLM spend and the shared question bank stay under my control | `LP-0002-03` |
| learner | to send feedback, or report a bad question, from inside the app | problems reach the admin with context, without deleting questions for everyone | `LP-0002-04` |
| admin | a per-user daily cap on LLM grading | self-signup cannot run up the platform's OpenRouter bill | `LP-0002-05` |
| learner, later phase | to plug in my own OpenRouter key and generate questions myself | I am not waiting on the admin | not filed |

- Order: `01` → `03` → `04`. `02` can land any time after `01`. An admin flag
  means nothing while anyone can sign in as any username, so `01` goes first.
  `04` uses `03`'s `admin_required` guard. `05` lands before `01`'s production
  cutover opens self-signup. That cutover runs as `LP-0007`.
- No artifact at the epic level. `LP-0002-02` carries the one visual choice.
- Workflow calls per story. Every story changes the schema, so each runs
  `schema-check` before its code lands, and each PRD story closes with a
  `prd-report` the user approves.

| Story | PRD | Artifact | Schema change (`schema-check`) |
| --- | --- | --- | --- |
| `01` | `docs/prd/LP-0002-01-google-sign-in.md` (approved, no console accounts) | No | `users.email`, unique `email_1`, and a migration that deletes username-only users |
| `02` | `docs/prd/LP-0002-02-law-onboarding.md` | Yes, built before the PRD | `users.study_law_types`, `users.onboarded_at` |
| `03` | No | No | `users.is_admin` |
| `04` | `docs/prd/LP-0002-04-feedback-to-admin.md` | No | New `feedback` collection |
| `05` | No | No | Only if the daily count needs a new field |

- Out of scope: password login, roles beyond learner and admin (a README
  non-goal), building BYOK, an admin dashboard, and billing.

## Acceptance Criteria

- [ ] All child stories are `resolved` or `wont_fix`.
- [ ] The BYOK phase is filed as its own ticket, or recorded as deferred in
      `docs/modules/question-gen/index.md`.
- [ ] `docs/modules/index.md` lists the modules the stories create: `auth`,
      `laws`, `question-gen`, and `feedback`.
- [ ] `pytest` green: covered by the child stories.
- [ ] `flake8` clean: covered by the child stories.
- [ ] Seen working: covered by each child story's smoke run.
- [ ] Docs synced: covered by the child stories' changelog entries.

## Open Questions

- None.

## Related Files

- `docs/issues/pending/LP-0002-invite-only-beta/`
- `routes/auth.py`, `services/auth.py`, `routes/admin.py`, `routes/quiz.py`
- `scripts/generate_questions_remote.py`
- `db/models.py`

## Handoff Appendix

### Settled Decisions

- SSO is Google sign-in, with accounts keyed by verified email in our own
  `users` collection. Decided by the user on 2026-10-16.
- No console account creation. `scripts/add_user.py` is deleted, and admin
  edits happen in Atlas. Decided by the user on 2026-10-17.
- Self-signup is allowed: any Google account with a verified email gets an
  account on first sign-in. This reverses invite-only. Decided by the user
  on 2026-10-16.
- From `LP-0002-01` on, smoke runs and `prd-report` walks sign in by hand,
  in the Playwright browser, with two dedicated test Google accounts that
  both sign themselves up (deleted from the local DB between runs to make
  them new again). No login bypass is added
  for testing. Decided by the user on 2026-10-16, and updated for
  self-signup.
- Feedback is an in-app form saved to Mongo. General feedback then opens the
  learner's Gmail compose, prefilled and addressed to the admin, and the
  server sends no email. The login page shows the admin email.
- The 📢 '回報題目問題' button files a report. It no longer deletes the
  question.

### Findings From Grounding (2026-10-16)

- `services/auth.py` `validate_user` signs in on username alone, with no
  password, on a public Heroku URL.
- `routes/admin.py` `/api/admin/init-laws` has no auth decorator.
- The 📢 button calls `DELETE /api/quiz/questions/<id>`, which soft-deletes a
  shared question for every user. Any signed-in user can call it.
- The law choice lives only in the Flask session (`current_law_type`,
  default `patent-act`).
- Short-answer grading (`routes/quiz.py:306`) calls OpenRouter on the
  platform key for every answer, so with self-signup any signed-in learner
  spends it. `LP-0002-05` caps it per user per day.
- Generation runs only from `scripts/`. `QuestionGenerator(api_key=...)` and
  `LLMClient(api_key=...)` already accept a per-instance key.

### Deferred Decisions

- **BYOK (later phase).** File it when the phase starts. It must decide:
  - how learner keys are stored (encrypted at rest, never logged, never
    returned to the client);
  - whether learner-generated questions join the shared bank or stay private
    to that learner;
  - per-learner cost and rate limits.
