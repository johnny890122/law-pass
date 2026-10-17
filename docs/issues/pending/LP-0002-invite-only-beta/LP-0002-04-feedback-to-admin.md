---
id: LP-0002-04
title: In-app feedback to the admin, and 📢 reports instead of deleting
type: story
status: pending
priority: high
created: 2026-10-16
resolved:
area: admin
parent: LP-0002
tags:
  - feedback
  - email
  - data-integrity
---

# In-app feedback to the admin, and 📢 reports instead of deleting

## Description

Learners have no way to reach the admin. The one report button they do have,
📢 '回報題目問題', soft-deletes the shared question for every user. Learners
need a feedback form that reaches the admin with context, and 📢 should file a
report instead of deleting.

## Details

- Current:
  - There is no feedback channel. UI copy sends learners to the admin with no
    way to reach them: '題目數量不足，請聯繫管理員生成更多題目。'
    (`quiz_config.html`, `routes/quiz.py`) and '如果您沒有帳號，請聯繫管理員'
    (`login.html`).
  - 📢 in `quiz_session.html` opens a confirm modal ('確定要刪除此題目嗎？',
    '永久刪除'). Confirming appeals the answer, which reverses its score, then
    calls `DELETE /api/quiz/questions/<id>`, which sets `is_deleted: true` for
    everyone. Any signed-in user can call that DELETE.
- Desired:
  - Add a new `feedback` collection with these fields: `user_id` (ObjectId),
    `kind` (`general` | `question`), `message`, `question_id` (hex str, for
    the `question` kind), `page` (URL path), `created_at`, and `status`
    (`open`). The id types follow the `data-model.md` conventions. It is the
    admin's record of every submission, read and closed in Atlas.
  - **General feedback.** A form reachable from every signed-in page. Its
    entry point sits in the header user menu (`base.html` `.user-menu`), next
    to the display name that `LP-0002-02` links to `/account`. Submitting it:
    1. POSTs to a new sign-in-only endpoint, which saves the `feedback` doc and
       returns its id.
    2. Opens a prefilled Gmail compose window for the learner, addressed to
       `ADMIN_EMAIL`. The subject and body carry the message, the page, and
       the feedback id. The learner presses send in their own Gmail.
  - **📢 report-a-question.** The modal asks for an optional reason. It keeps
    the appeal step (score reversed, move on to the next question), then saves
    a `kind: question` feedback doc. It does **not** open Gmail, so the quiz
    is not interrupted. It no longer calls DELETE, and the copy drops
    '永久刪除' and '此操作無法復原'.
  - `DELETE /api/quiz/questions/<id>` becomes admin-only, using
    `admin_required` from `LP-0002-03`.
  - **Login page.** Next to '如果您沒有帳號，請聯繫管理員', show `ADMIN_EMAIL`
    as a visible address with a `mailto:` link, for visitors who have no
    account and so cannot use the form.
  - Signed-in copy that says '請聯繫管理員' links to the form.
  - The app sends no email itself: no SMTP, no email API, and no mail secret.
    `ADMIN_EMAIL` is the only new env var, added to `.env.example` and the
    Heroku config.
- Schema change: the new `feedback` collection goes through `schema-check`,
  which also settles whether it needs any index beyond `_id_`.
- PRD: `docs/prd/LP-0002-04-feedback-to-admin.md`.
- No artifact — the form reuses the existing `modal-overlay` pattern from
  `quiz_session.html`, and its entry point joins the existing user menu, so
  there is no layout choice to make.
- Depends on `LP-0002-03` for `admin_required`.
- Out of scope: an admin inbox UI, replying in-app, attachments, and
  server-side email.

## Acceptance Criteria

- [ ] Submitting general feedback stores a `feedback` doc with the user and the
      page, then opens Gmail compose addressed to `ADMIN_EMAIL`, with the
      message, page, and feedback id prefilled.
- [ ] 📢 stores a `kind: question` report, reverses that answer's score, and
      moves on without opening Gmail. The question stays in the bank, with
      `is_deleted` unchanged.
- [ ] A non-admin `DELETE /api/quiz/questions/<id>` returns 403.
- [ ] A signed-out visitor sees `ADMIN_EMAIL` on the login page.
- [ ] `schema-check` passed. `data-model.md` has a `feedback` section, with a
      Change Log row.
- [ ] `pytest` green — covered by `tests/test_feedback.py`.
- [ ] `flake8` clean.
- [ ] Seen working in the running app, signed in with a test Google
      account:
  - Send general feedback from the user menu. The doc appears in Mongo, and
    the new tab's URL is a Gmail compose addressed to `ADMIN_EMAIL` with the
    message, page, and id prefilled. There is no need to press send.
  - Report a question mid-quiz. The doc appears, and the quiz carries on with
    no new tab.
  - Sign out. The login page shows the admin email.
- [ ] Docs synced: `docs/modules/feedback/index.md` (new),
      `docs/modules/index.md`, and `docs/modules/db/data-model.md` (through
      `schema-check`), plus a changelog entry.
- [ ] Report at `docs/reports/LP-0002-04-feedback-to-admin/report.md` is
      approved.

## Open Questions

- Spam and rate limits were out of scope because the beta was invite-only.
  With self-signup (`LP-0002-01`), any Google account can file feedback. Are
  they still out of scope?
- The login page shows `ADMIN_EMAIL` "for visitors who have no account and so
  cannot use the form". With self-signup, any visitor can get an account by
  signing in. Is the public address still wanted?

## Related Files

- `templates/quiz_session.html`
- `templates/base.html`
- `templates/login.html`
- `templates/quiz_config.html`
- `routes/quiz.py`
- `routes/feedback.py` (new)
- `static/js/main.js`
- `db/models.py`
- `.env.example`
- `tests/test_feedback.py`
- `docs/prd/LP-0002-04-feedback-to-admin.md`
- `docs/modules/db/data-model.md`

## Handoff Appendix

### Settled Decisions

Decided by the user on 2026-10-16:

- Email goes through the learner's own Gmail, opened prefilled by the app. The
  server sends nothing.
- Only general feedback opens Gmail. 📢 reports are saved to Mongo only.
- The login page shows the admin email to visitors without an account.
- The general-feedback entry point goes in the header user menu, so the
  ticket needs no artifact.

### Behavior Details

- The doc is saved before Gmail opens. If the learner never presses send, or
  their Google account has no Gmail, the feedback is still in Mongo and is not
  lost.
- Compose URL: `https://mail.google.com/mail/?view=cm&fs=1&to=…&su=…&body=…`,
  with every parameter URL-encoded.
- Popup blockers: `window.open` called after an `await` is usually blocked.
  Open the tab synchronously in the click handler, then point it at the
  compose URL once the POST returns the feedback id.
- Showing `ADMIN_EMAIL` on the public login page exposes it to scrapers. The
  user accepted this.

### Test Scenarios

- `tests/test_feedback.py`:
  - A signed-in POST of general feedback → 201 with the id, and one `feedback`
    doc with `user_id`, `page`, and `status: open`.
  - A signed-out POST → refused.
  - A question report → `kind: question` with `question_id`, and the
    question's `is_deleted` stays false.
  - A non-admin DELETE of a question → 403, and the question is unchanged.
  - The login page renders `ADMIN_EMAIL`.
