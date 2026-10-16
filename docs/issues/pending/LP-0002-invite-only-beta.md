---
id: LP-0002
title: Invite-only beta user stories
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

# Invite-only beta user stories

## Description

The MVP serves a few hand-added users, but it trusts any typed username, has no
admin role, and gives learners no way to reach the admin. This epic records the
product's user stories for an invite-only beta: real sign-in, per-learner law
setup, admin-controlled generation, and a feedback line to the admin.

## Details

- Phase rules:
  - **Invite-only.** No self-signup. The admin provisions every account from
    the console (`scripts/add_user.py` or Atlas).
  - **Admin-only generation.** Only the admin triggers question generation,
    using the platform OpenRouter key. Learners bringing their own key comes in
    a later phase, and nothing built now may block it.
- User stories, in roadmap form:

| As a… | I want… | So that… | Ticket |
| --- | --- | --- | --- |
| learner | to sign in with my Google account | only invited people get in, with no extra password | `LP-0002-01` |
| learner, on first login | to pick the laws I am studying | the app starts on my exam's laws, not 專利法 by default | `LP-0002-02` |
| admin | to be the only one who can generate questions or call admin endpoints | LLM spend and the shared question bank stay under my control | `LP-0002-03` |
| learner | to send feedback, or report a bad question, from inside the app | problems reach the admin with context, without deleting questions for everyone | `LP-0002-04` |
| learner, later phase | to plug in my own OpenRouter key and generate questions myself | I am not waiting on the admin | not filed |

- Order: `01` → `03` → `04`. `02` can land any time after `01`. An admin flag
  means nothing while anyone can sign in as any username, so `01` goes first.
  `04` uses `03`'s `admin_required` guard.
- No artifact at the epic level. `LP-0002-02` carries the one visual choice.
- Out of scope: self-signup, password login, roles beyond learner and admin (a
  README non-goal), building BYOK, an admin dashboard, and billing.

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
- `scripts/add_user.py`, `scripts/generate_questions_remote.py`
- `db/models.py`

## Handoff Appendix

### Settled Decisions

- SSO is Google sign-in, allowlisted by email in our own `users` collection.
  "Console" means our script or Atlas, not an identity vendor's dashboard.
  Decided by the user on 2026-10-16.
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
- Generation runs only from `scripts/`. `QuestionGenerator(api_key=...)` and
  `LLMClient(api_key=...)` already accept a per-instance key.

### Deferred Decisions

- **BYOK (later phase).** File it when the phase starts. It must decide:
  - how learner keys are stored (encrypted at rest, never logged, never
    returned to the client);
  - whether learner-generated questions join the shared bank or stay private
    to that learner;
  - per-learner cost and rate limits.
