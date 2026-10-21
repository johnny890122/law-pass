---
id: LP-0004-07
title: Adopt the dense-tabbar layout and teal role-hues palette on every page
type: story
status: resolved
priority: medium
created: 2026-10-19
resolved: 2026-10-20
area: ui
parent: LP-0004
tags:
  - design-system
  - adoption
  - rwd
---

# Adopt the dense-tabbar layout and teal role-hues palette on every page

## Description

The user picked the design system in three steps: the `dense-tabbar` layout
(`LP-0004-05`), the `role-hues` palette and its less-AI frame
(`LP-0004-06`), and teal as the main color (`LP-0004-08`). Now they want it
in the real app, and every page moves onto the token contract in one story.

## Details

- Current:
  - **Assets.** `templates/base.html` loads the MUI 0.10.3 CSS and JS from a
    CDN, the Figma `design-tokens.css`, and `style.css` (2,223 lines).
    `style.css` opens with an alias layer that maps 15 legacy names onto
    Figma tokens, and its rules read 31 token names in all.
    `design-tokens-dark.css` is not wired.
  - **Header.** Two rows on phone, one row from 768px, per
    `docs/modules/ui/index.md`.
  - **Dashboard.** `/` renders `dashboard.html` with no data: three
    buttons, plus tips under an emoji heading, using inline styles.
  - **Inline styles and colors.**
    - `login.html` stands alone, outside `base.html`, with 28 hard-coded
      colors.
    - Templates carry 75 inline `style=` attributes, 31 of them in
      `law_detail.html`.
    - `laws`, `law_detail`, `quiz_config`, `quiz_session`, `my_questions`,
      and `question_bank` build markup in inline JS through `innerHTML`.
- Desired:
  - **Tokens.** The values of
    `.claude/skills/neta-design/tokens/role-hues-teal.css` become the app's
    one token file in `static/css/`. `design-tokens.css` and
    `design-tokens-dark.css` are deleted. The system tier and the
    `dense-tabbar` and `role-hues` rules from
    `artifacts/LP-0004-08-main-color/` move into `static/css/`. The PRD
    sets the file split.
  - **Contract names everywhere.** `style.css`, every template, and the
    markup built in JS read contract names. The legacy alias layer is gone,
    and no color literal remains outside the token file.
  - **Shell.** `base.html` becomes the `dense-tabbar` shell on every page:
    - Below 1024px: a top bar and a bottom tab bar.
    - From 1024px: a left sidebar.
    - It keeps every control: logo, 首頁 法條瀏覽 題庫 我的進度, the
      law-type select, 中/EN, the user name, and logout.
    - The MUI CDN CSS and JS are dropped.
  - **Dashboard.** `/` loads `get_progress_summary(user_id, None, law_type)`
    (all time) and renders the five-number ledger, the start block, and the
    tips. This is a route change.
  - **Every page follows the `role-hues` frame,** per the `LP-0004-06` and
    `LP-0004-08` `DECISION.md` files:
    - Containers: ledger, panel, and sheet.
    - Index tabs instead of pills.
    - Flags with fixed meanings: teal for actions, 選擇題, and 作答題數;
      blue for 法條; magenta for 簡答題; flamingo for the streak.
    - Status colors stay semantic. All text is 黑體. Emoji section markers
      are dropped.
  - **Pages in scope:** dashboard, laws, law detail, quiz config, the quiz
    session (question and graded), my questions, question bank, progress,
    and login. The progress charts read `--color-data-1` and
    `--color-data-2` through `getComputedStyle`.
  - **Graded quiz.** The teal tint and the success tint are kept apart, per
    `LP-0004-08`'s watch item. The PRD decides how.
- No artifact — the look is decided by `LP-0004-05`, `LP-0004-06`, and
  `LP-0004-08`. Pages without a mock (laws, quiz config, my questions,
  question bank, progress, and login) use the same container vocabulary.
  The `prd-report` shows each page for sign-off.
- PRD: `docs/prd/LP-0004-07-adopt-design-system.md`.
- Out of scope:
  - Dark mode, and any new page or route beyond `/` loading data.
  - API response changes.
  - Copy changes beyond dropping the emoji section markers.
  - `LP-0002-02`'s onboarding route, which lands on whichever shell is
    current.

## Acceptance Criteria

- [x] `static/css/` holds the teal values file and no Figma token file.
      `base.html` links no MUI asset.
- [x] The `neta-design` hex grep prints nothing for `templates/`,
      `static/js/`, and every `static/css/` file except the values file.
- [x] `/` renders the five all-time progress numbers for the current law
      type. A user with no records gets the PRD's defined state.
- [x] Every page renders in the `dense-tabbar` shell with every `base.html`
      control. `login.html` renders on the tokens.
- [x] Every page passes the `docs/modules/ui/index.md` check at phone
      390x844, tablet 768x1024, and desktop 1440x900: no page scroll and no
      overflowing element.
- [x] The role map holds on every page. Each hue has one meaning, and
      status colors are only status.
- [x] `pytest` green — covered by `tests/test_app.py`. `GET /` with seeded
      daily stats renders the five numbers. A user with no stats gets the
      PRD's empty state.
- [x] `flake8` clean.
- [x] Seen working in the running app: `python app.py`, then every page at
      all three viewports in Playwright. Each page passes the
      `docs/modules/ui/index.md` check, and the screenshots are looked at.
- [x] Docs synced: `docs/modules/ui/index.md` (the shell, the container
      vocabulary, the role map, and where tokens live) and a changelog
      entry.
- [x] PRD tickets only: report at
      `docs/reports/LP-0004-07-adopt-design-system/report.md` is approved.

## Open Questions

- None.

## Related Files

- `templates/` (all 10)
- `static/css/style.css`
- `static/css/design-tokens.css`
- `static/css/design-tokens-dark.css`
- `static/js/main.js`
- `routes/frontend.py`
- `services/progress.py`
- `tests/test_app.py`
- `docs/modules/ui/index.md`
- `.claude/skills/neta-design/tokens/role-hues-teal.css`
- `artifacts/LP-0004-05-design-directions/DECISION.md`
- `artifacts/LP-0004-06-color-variants/DECISION.md`
- `artifacts/LP-0004-08-main-color/` (`DECISION.md`, `system.css`,
  `dense-tabbar-layout.css`, `role-hues-color.css`)
- `docs/prd/LP-0002-02-law-onboarding.md` (also changes `/`)

## Handoff Appendix

### Settled Decisions

Confirmed with the user on 2026-10-19:

- Teal `role-hues` is the palette (`LP-0004-08`).
- Full adoption: all pages in one story, not the shell and dashboard first.
- The dashboard's five numbers cover all time. `/progress` keeps its
  7 / 30 / all-time switch.
- From the epic: `design-tokens*.css` are retired, the MUI CDN is dropped,
  and all text is 黑體.

### Deferred Decisions

- Dark mode: no ticket yet.

## Resolution

Every page now runs on the teal `dense-tabbar` / `role-hues` design system:
`static/css/tokens.css` is the one token file and the only home of a color
literal, MUI and the Figma token files are gone, and `/` opens on the five
all-time progress numbers. Dark mode and hanging paragraph numbers were left
out. See [the changelog entry](../../../changelog/2026-10-20-adopt-design-system.md)
and [the approved report](../../../reports/LP-0004-07-adopt-design-system/report.md).
