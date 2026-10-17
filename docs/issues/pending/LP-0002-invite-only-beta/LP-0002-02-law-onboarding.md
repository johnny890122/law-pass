---
id: LP-0002-02
title: First-login onboarding to set your name and pick the laws you study
type: story
status: pending
priority: medium
created: 2026-10-16
resolved:
area: laws
parent: LP-0002
tags:
  - onboarding
  - account
  - artifact
---

# First-login onboarding to set your name and pick the laws you study

## Description

Learners prepare for different exams, yet every login starts on 專利法, and the
law choice lives only in the session cookie. A first-login step lets each
learner pick their laws once and keeps that choice on their account. The
header switcher then shows only those laws, and the learner can change them on
an account settings page. Since `LP-0002-01` allows self-signup, onboarding is
also where a new learner can replace the random display name they start with.

## Details

- Current:
  - `current_law_type` is stored only in the Flask session
    (`services/auth.py` `get_current_law_type`, default `patent-act`).
  - The header switcher in `templates/base.html` is filled by JS from
    `GET /api/law-types`, which returns all four `LAW_TYPES`.
    `POST /api/law-types/select` accepts any of them.
  - Nothing is stored per user, and there is no account page.
- Desired:
  - New fields on `users`:
    - `study_law_types`: a list of `LAW_TYPES` keys. Empty means all laws.
    - `onboarded_at`: a datetime, set when the learner saves or skips.
      Missing means the learner has not onboarded yet.
  - After sign-in, a learner with no `onboarded_at` lands on onboarding before
    the dashboard.
    - **Name (optional):** the learner can change their display name, saved
      to `users.display_name` and shown in the header. A self-signed-up
      learner (`LP-0002-01`) starts with a random name. Leaving it, or
      skipping onboarding, keeps the current name.
    - **Pick:** saves `study_law_types` and sets `current_law_type` to the
      first chosen law.
    - **Skip**, for when none of the laws fit: saves `onboarded_at` with
      `study_law_types` empty. The learner keeps all laws and is not asked
      again.
  - The header switcher lists only the learner's chosen laws, or all laws if
    the list is empty. The server enforces this. `GET /api/law-types` filters
    the list, and `POST /api/law-types/select` rejects a law outside the
    learner's set.
  - `current_law_type` always stays inside the set. At login, and after a
    settings change, a value outside the set resets to the first chosen law.
  - New account settings page (`/account`), linked from the header user menu
    (`#user-display-name`). This phase it holds only the law picker, reusing
    the onboarding component. Saving updates `study_law_types`, and clearing
    every law means all laws.
- Schema change: both new `users` fields go through `schema-check`. A missing
  `study_law_types` reads as empty (all laws), and a missing `onboarded_at`
  means not onboarded, so nothing is backfilled. Every account created after
  `LP-0002-01` comes from self-signup, and onboards on its
  first login.
- PRD: `docs/prd/LP-0002-02-law-onboarding.md`. Build the artifact before the
  PRD. The pick decides whether onboarding is its own route (variant A) or
  renders on the dashboard (B, C), so the PRD's route contracts follow
  `DECISION.md`.
- Artifact required. The visual question: on a phone, how heavy should the
  first-login law picker be? Variants:
  - **A. Full page.** One card per law, with its 中文 name and article count
    from `get_available_law_types`. Clearest choice, but adds a whole extra
    screen before the first quiz.
  - **B. Modal over the dashboard.** A checklist in the existing
    `modal-overlay` pattern. Lightest, but easy to dismiss without reading.
  - **C. Dashboard empty state.** Law chips inline where the stats would go.
    No interruption, but the most likely to be ignored.
- Not open in any variant:
  - UI copy is 繁體中文, and the list comes from `LAW_TYPES`.
  - Styles use `static/css/design-tokens.css`, and everything works at 390px
    wide.
  - A visible skip action for learners whose laws are not listed.
  - A display-name field.
- The account page reuses the winning picker, so it gets no artifact of its
  own.
- Out of scope:
  - exam date, study goals, and question-language preference;
  - editing `display_name` on the account page after onboarding;
  - adding new law types, and asking the admin for a missing law (that goes
    through the `LP-0002-04` feedback form);
  - the `?law_type=` query param on `routes/quiz.py:75` and
    `routes/laws.py:80`, `:353`, and `:811`, which still reads any law (see
    Settled Decisions).

## Acceptance Criteria

- [ ] A learner with no `onboarded_at` is sent to onboarding after sign-in.
- [ ] A display name changed in onboarding is saved to `users.display_name`
      and shows in the header. Leaving it unchanged, or skipping, keeps the
      current name.
- [ ] Picking laws stores `study_law_types` and `onboarded_at`, and both
      survive logout and login.
- [ ] Skipping stores `onboarded_at` with `study_law_types` empty. The learner
      sees all laws and is not asked again.
- [ ] The header switcher shows only the chosen laws.
      `POST /api/law-types/select` with a law outside the set returns 400.
- [ ] Each login starts on the first chosen law, and never on a law outside
      the set.
- [ ] `/account` changes the chosen laws, and the switcher updates to match.
- [ ] Variants in `artifacts/LP-0002-02-law-onboarding/` screenshot at phone
      (390x844), tablet (768x1024), and desktop (1440x900), reviewed with the
      user; choice recorded in `DECISION.md`.
- [ ] `schema-check` passed. `data-model.md` lists `study_law_types` and
      `onboarded_at`, with a Change Log row.
- [ ] `pytest` green — covered by `tests/test_onboarding.py`.
- [ ] `flake8` clean.
- [ ] Seen working in the running app, signed in with a test Google
      account. To make it fresh again between runs, `$unset` its
      `onboarded_at` and `study_law_types` in the local DB.
  - Fresh: pick 訴願法 and 行政訴訟法. The switcher shows only those two, and
    logging out and back in keeps them.
  - Fresh again: skip, and all four laws show.
  - On `/account`, adding 專利法 makes it appear in the switcher.
- [ ] Docs synced: `docs/modules/laws/index.md` (new),
      `docs/modules/index.md`, and `docs/modules/db/data-model.md` (through
      `schema-check`), plus a changelog entry.
- [ ] Report at `docs/reports/LP-0002-02-law-onboarding/report.md` is
      approved.

## Open Questions

- None.

## Related Files

- `services/auth.py`
- `routes/auth.py`
- `routes/frontend.py`
- `routes/law_types.py`
- `templates/base.html`
- `templates/onboarding.html` (new, variant A only)
- `templates/account.html` (new)
- `static/js/main.js`
- `db/models.py`
- `tests/test_onboarding.py`
- `artifacts/LP-0002-02-law-onboarding/`
- `docs/prd/LP-0002-02-law-onboarding.md`
- `docs/modules/db/data-model.md`

## Handoff Appendix

### Settled Decisions

Decided by the user on 2026-10-16:

- The header switcher is limited to the chosen laws.
- Onboarding can be skipped when none of the laws fit, and skipping keeps all
  laws.
- The pick is changed later on an account settings page.
- The name step is optional. Leaving it unchanged, or skipping onboarding,
  keeps the current `display_name`. Decided by the user on 2026-10-17.
- The study set is a UX filter on the switcher and `current_law_type`, not
  access control. The `?law_type=` query param stays open: the frontend never
  sends it, and law content is shared.

### Behavior Details

- Recording `onboarded_at` on skip is what stops a skipped learner from being
  asked again at every login.
- An empty `study_law_types` means "all laws" in every place that reads it:
  the switcher, `select`, and the login reset. Treat it the same way
  everywhere.

### Test Scenarios

- `tests/test_onboarding.py`:
  - A user with no `onboarded_at` → after login, the dashboard redirects to
    onboarding.
  - Save the name `Alice` → `users.display_name == 'Alice'`, and the session's
    `display_name` matches on the next request.
  - Save `['administrative-appeal']` → `GET /api/law-types` returns only that
    law, and `current_law_type` is `administrative-appeal`.
  - `POST /api/law-types/select` with `patent-act` while it is not chosen →
    400.
  - Skip → `onboarded_at` set, `study_law_types == []`, all four laws
    returned, and no redirect on the next login.
  - The session holds a law that was removed on `/account` → the next request
    resets it to the first chosen law.
