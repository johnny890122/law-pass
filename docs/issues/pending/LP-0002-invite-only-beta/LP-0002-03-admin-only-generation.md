---
id: LP-0002-03
title: Admin role, guarded admin endpoints, admin-only generation
type: story
status: pending
priority: high
created: 2026-10-16
resolved:
area: admin
parent: LP-0002
tags:
  - admin
  - security
  - question-gen
---

# Admin role, guarded admin endpoints, admin-only generation

## Description

Generation spends the platform's OpenRouter budget and fills the question bank
every learner shares, so only the admin may trigger it in this phase. Yet
there is no admin role, and `/api/admin/init-laws` is open to anyone, even
signed-out visitors.

## Details

- Current:
  - `users` has no role, and `/api/admin/init-laws` (`routes/admin.py`) has no
    auth decorator.
  - Generation runs only from `scripts/generate_questions_remote.py` and
    `scripts/generate_examination_questions.py`, using `OPENROUTER_API_KEY`.
    No route calls `QuestionGenerator`, so learners can't trigger it today, but
    only by accident.
  - `QuestionGenerator(api_key=...)` and `LLMClient(api_key=...)` already take
    a key per instance.
- Desired:
  - Add `users.is_admin` (bool, default false). It is set only from the
    console, in Atlas (`scripts/add_user.py` was deleted on 2026-10-17), and no route ever
    writes it.
  - Add an `admin_required` decorator in `services/auth.py`. Signed-out
    requests are treated as `login_required` treats them (302 to
    `/auth/login`), and a signed-in non-admin gets 403. It reads `is_admin`
    from `users` on each request, not from the session, so a console change
    applies on the next request.
  - Every `/api/admin/*` route uses it.
  - Generation is triggered only through the CLI scripts in `scripts/`, run by
    the admin. No route calls `QuestionGenerator`, including admin routes, and
    the app has no in-app generation page this phase. Decided by the user on
    2026-10-16.
  - BYOK seam: the key stays an explicit `api_key` argument to
    `QuestionGenerator` and `LLMClient`, and the later BYOK phase passes a
    learner's key through that same argument. Add no per-user key storage, no
    key settings UI, and no key-resolver abstraction now.
- Schema change: `users.is_admin` goes through `schema-check`. A missing
  field reads as false, so nothing is backfilled.
- No PRD — one console-set flag, one decorator, and one guarded route, and
  Details states the whole contract.
- No artifact — no screen changes.
- Out of scope:
  - BYOK itself, an admin dashboard or in-app generation page, and roles
    beyond learner and admin.
  - `init-laws` upserts with `{"article_number": ...}` only, so a re-run can
    overwrite another law type's or language's article. That is a separate
    data bug to file as its own ticket.

## Acceptance Criteria

- [ ] `POST /api/admin/init-laws` redirects to `/auth/login` when signed out,
      returns 403 for a signed-in non-admin, and runs for the admin.
- [ ] `is_admin` can be set only from the console. No route writes it.
- [ ] No module under `routes/` imports `QuestionGenerator`.
- [ ] `schema-check` passed. `data-model.md` lists `is_admin`, with a Change
      Log row.
- [ ] `pytest` green — covered by `tests/test_admin.py`, with the law parser
      stubbed and no OpenRouter calls.
- [ ] `flake8` clean.
- [ ] Seen working in the running app, against a throwaway local DB, because
      `init-laws` can overwrite other law types' articles (see Out of scope).
      Signed in with a test Google account, calling
      `/api/admin/init-laws` returns 403. After `is_admin` is set on that
      account in the DB, the next call runs.
- [ ] Docs synced: `docs/modules/auth/index.md` (admin role),
      `docs/modules/question-gen/index.md` (new; records the admin-only rule,
      the platform key, and the `api_key` seam for BYOK), and
      `docs/modules/db/data-model.md` (through `schema-check`), plus a
      changelog entry.

## Open Questions

- None.

## Related Files

- `services/auth.py`
- `routes/admin.py`
- `scripts/generate_questions_remote.py`
- `scripts/generate_examination_questions.py`
- `services/question_gen.py`
- `services/llm_client.py`
- `db/models.py`
- `tests/test_admin.py`
- `docs/modules/db/data-model.md`
