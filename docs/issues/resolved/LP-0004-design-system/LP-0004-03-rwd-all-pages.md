---
id: LP-0004-03
title: Every page holds at phone, tablet, and desktop
type: story
status: resolved
priority: medium
created: 2026-10-17
resolved: 2026-10-18
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

- [x] Every page × three viewports shows no page scroll and no overflowing
      element, recorded as a table in `## Resolution` or a linked note.
- [x] `style.css` uses only `min-width: 768px` and `min-width: 1024px`
      media queries.
- [x] Every inline `style=` the audit flagged as breaking layout now lives
      in `style.css`. Only the pager row in `question_bank.html` and
      `my_questions.html` was flagged; it is now `.pager`.
- [x] The `CLAUDE.md` done gate names the three viewports for template and
      CSS changes.
- [x] `pytest` green: template and CSS only, so no new test. The existing
      page-render tests in `tests/test_app.py` confirm nothing regressed.
      101 passed.
- [x] `flake8` clean.
- [x] Seen working: every page opened in the running app with Playwright
      at 390x844, 768x1024, and 1440x900 and checked by eye. A local
      learner was signed in by session cookie on a throwaway local DB seeded
      with the 168 patent-act articles and 12 fixture questions.
- [x] Docs synced: create `docs/modules/ui/index.md` with the breakpoint
      rule and viewport set, add its row to `docs/modules/index.md`, and
      write a changelog entry.

## Open Questions

- None.

## Resolution

`style.css` is mobile-first with only `min-width: 768px` and `1024px`. The
tablet nav no longer wraps, the progress charts fill their cards, and the
pager is a shared class. See
[2026-10-18-rwd-all-pages.md](../../../changelog/2026-10-18-rwd-all-pages.md).

Audit after the fix. ✓ means no page scroll, no overflowing element, and no
wrapped or clipped nav, plus a look at the screenshot:

| Page / state | Phone 390x844 | Tablet 768x1024 | Desktop 1440x900 |
| --- | --- | --- | --- |
| `login` | ✓ | ✓ | ✓ |
| `dashboard` | ✓ | ✓ | ✓ |
| `laws` | ✓ | ✓ | ✓ |
| `law_detail` (第 90 條, answered question) | ✓ | ✓ | ✓ |
| `question_bank` | ✓ | ✓ | ✓ |
| `my_questions` (starred tab) | ✓ | ✓ | ✓ |
| `quiz_config` | ✓ | ✓ | ✓ |
| `quiz_session`, MCQ question | ✓ | ✓ | ✓ |
| `quiz_session`, MCQ graded feedback | ✓ | ✓ | ✓ |
| `quiz_session`, short-answer question | ✓ | ✓ | ✓ |
| `progress` (charts) | ✓ | ✓ | ✓ |

Before the fix, the scripted check also passed everywhere. The defects
showed only in the screenshots: the tablet nav wrapped, the charts were
drawn 520px wide at tablet and desktop, and the phone pager buttons wrapped.
Short-answer graded feedback was not audited because OpenRouter is unset
locally.

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
