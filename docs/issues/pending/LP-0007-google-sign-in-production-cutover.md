---
id: LP-0007
title: Production cutover for Google sign-in
type: todo
status: pending
priority: high
created: 2026-10-17
resolved:
area: deploy
tags:
  - sso
  - migration
  - heroku
---

# Production cutover for Google sign-in

## Description

`LP-0002-01`'s code changes how everyone signs in and deletes username-only
users. Its production rollout is destructive, and it waits on two other
tickets, so it runs here, separate from the code ticket.

## Details

- Runs the Rollout section of `docs/prd/LP-0002-01-google-sign-in.md`
  against production, in its order:
  1. Register the Heroku app's `https://<app>.herokuapp.com/auth/google/callback`
     on the OAuth client, and publish the consent screen "In production".
  2. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` on Heroku.
  3. `mongodump` the seven affected collections. This is the only way back.
  4. Run `scripts/migrations/20261016_remove_username_only_users.py`: a dry
     run first, then `--apply`.
  5. Cut off the old `patent-act-15774ac83829` app by rotating the Atlas user
     its `MONGO_URI` uses, after confirming the new app uses its own Atlas
     user.
  6. Run the `schema-check` preflight on production for `email`.
  7. Deploy. `init_db()` builds `email_1`.
  8. Rotate `SECRET_KEY`.
  9. Smoke test on Heroku with two test accounts that sign themselves up.
  10. Set `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and
      `OPENROUTER_GRADING_MODEL`, only after `LP-0002-05`'s grading cap is
      deployed. Deferred from `LP-0008` on 2026-10-17. The grading var is
      required, because the code default is no longer listed on OpenRouter.
- Changed on 2026-10-17 (`LP-0003`): `law-pass` starts on a new, empty
  Atlas database, because the old one is unreachable. Its only users are
  the ones `scripts/add_user.py` creates before the cutover, and the old app
  does not share it. Steps 3–6 were written for a shared production
  database with real users.
- Ran early on 2026-10-17, at the user's request: step 1 (the Heroku
  callback registered, consent-screen status not checked), step 2 (the user
  set the Google vars), and step 7 (`infra` merged to `main` and deployed).
  All came before `LP-0002-05`. One account has signed itself up over
  `https://`, so step 9 still needs the second.
- Prerequisites: `LP-0003` (the new Heroku app and CI) and `LP-0002-05` (the
  per-user daily grading cap) have landed, and `LP-0002-01` is resolved.
- Steps 3–5, 7, and 8 are destructive or outward-facing. Each runs only on
  the user's explicit go-ahead at that step.
- This ticket owns the production `Ran` cell of `LP-0002-01`'s Change Log row
  in `docs/modules/db/data-model.md`. It fills that cell with the Heroku
  migration and preflight results.
- No PRD — it executes `LP-0002-01`'s approved Rollout.
- No artifact — no screen changes.
- Out of scope: code changes. A defect found during the cutover gets its own
  ticket.

## Acceptance Criteria

- [ ] The dump of the seven collections is taken before `--apply`, and where
      it is kept is recorded here.
- [ ] Migration dry-run counts are recorded, then `--apply` runs, and a
      second dry run reports zero.
- [ ] No username-only user remains in production `users`.
- [ ] The old app can no longer reach the database, and the new app can.
- [ ] The `email` preflight finds no duplicates and no document without an
      email.
- [ ] Deployed: the boot log shows `init_db()` completing, and `SECRET_KEY`
      is rotated.
- [ ] The three OpenRouter vars are set only after `LP-0002-05` is deployed,
      and one answer is graded on Heroku.
- [ ] `pytest` and `flake8`: none — no code changes.
- [ ] Seen working on Heroku: two test accounts sign themselves up over
      `https://`. A logout then shows Google's account chooser.
- [ ] Docs synced: `docs/modules/db/data-model.md`'s `LP-0002-01` row has its
      production `Ran` cell filled, plus a changelog entry for the cutover.

## Open Questions

- With the database starting empty, which of steps 3–6 still run? Step 5
  (cutting off the old app) protects nothing now. Steps 3, 4, and 6 apply
  only to the users `add_user.py` creates before the cutover.

## Related Files

- `docs/prd/LP-0002-01-google-sign-in.md` (Rollout)
- `scripts/migrations/20261016_remove_username_only_users.py`
- `docs/modules/db/data-model.md`
- `docs/issues/resolved/LP-0003-heroku-ci-cd.md`
- `docs/issues/resolved/LP-0008-heroku-config-vars.md`
- `docs/issues/pending/LP-0002-invite-only-beta/LP-0002-05-grading-daily-cap.md`

## Handoff Appendix

### Settled Decisions

- The production cutover is split out of `LP-0002-01` into this ticket.
  Decided by the user on 2026-10-17.
