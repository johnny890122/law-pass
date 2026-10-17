---
id: LP-0004-03
title: Every page holds at phone, tablet, and desktop
type: story
status: pending
priority: medium
created: 2026-10-17
resolved:
area: ui
parent: LP-0004
tags:
  - rwd
  - design-system
---

# Every page holds at phone, tablet, and desktop

## Description

Learners study on phones and tablets, but the layout was only ever checked
at phone and desktop, and the CSS grew four breakpoint styles. This story
makes every page hold at 390x844, 768x1024, and 1440x900 on the current
CSS, before the design system lands.

## Details

- Current:
  - `style.css` has `max-width: 640px` (twice), `max-width: 767px`,
    `min-width: 768px` (three times), and `min-width: 1024px`.
  - Inline `style=` counts: `law_detail.html` 31, `question_bank.html` 15,
    `my_questions.html` 14, `quiz_session.html` 8, `quiz_config.html` 6,
    `dashboard.html` 5.
  - `login.html` has its own `<head>` rather than extending `base.html`.
  - The tablet viewport has never been checked.
- Desired:
  - **Audit** every page in `templates/` (`login`, `dashboard`, `laws`,
    `law_detail`, `question_bank`, `my_questions`, `quiz_config`,
    `quiz_session`, `progress`) at all three viewports, including the quiz
    session's question and graded-feedback states. Use the verify
    `browser_evaluate` from the artifact skill (no page scroll, no
    overflowing element), plus a look for clipped nav, unreadable long law
    text, and tables wider than the screen.
  - **Fix** what the audit finds. Go mobile-first with only
    `min-width: 768px` and `min-width: 1024px`, folding the `640px` and
    `767px` `max-width` queries into them. Move inline styles that break
    layout into `style.css`.
  - **Hold it:** `CLAUDE.md` done gate item 3 says a template or CSS change
    is seen at all three viewports.
  - No visual redesign: same look and same tokens.
- No artifact — the fixes keep the existing look. A page whose phone layout
  turns out to need a real choice (nav collapse, for example) is split into
  its own ticket with a `neta-design` variants pass, not decided here.
- No PRD — CSS and template fixes with no route or data change.
- Out of scope: token changes, restyling, other breakpoints, and dark mode.

## Acceptance Criteria

- [ ] Every page × three viewports shows no page scroll and no overflowing
      element, recorded as a table in `## Resolution` or a linked note.
- [ ] `style.css` uses only `min-width: 768px` and `min-width: 1024px`
      media queries.
- [ ] Every inline `style=` the audit flagged as breaking layout now lives
      in `style.css`.
- [ ] The `CLAUDE.md` done gate names the three viewports for template and
      CSS changes.
- [ ] `pytest` green: template and CSS only, so no new test. The existing
      page-render tests in `tests/test_app.py` confirm nothing regressed.
- [ ] `flake8` clean.
- [ ] Seen working: every page opened in the running app with Playwright
      at 390x844, 768x1024, and 1440x900 and checked by eye.
- [ ] Docs synced: create `docs/modules/ui/index.md` with the breakpoint
      rule and viewport set, add its row to `docs/modules/index.md`, and
      write a changelog entry.

## Open Questions

- None.

## Related Files

- `static/css/style.css`
- `templates/`
- `CLAUDE.md`
- `docs/modules/ui/index.md`
- `docs/modules/index.md`

## Handoff Appendix

### Test Scenarios

- The audit needs a signed-in local session and a law with generated
  questions, so that `quiz_session`, `question_bank`, and `my_questions`
  render real content. Google sign-in (`LP-0002-01`) means a provisioned
  local account. If none is available, say so rather than auditing empty
  states only.
