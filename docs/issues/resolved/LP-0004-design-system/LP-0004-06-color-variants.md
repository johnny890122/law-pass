---
id: LP-0004-06
title: Three color variants on the dense-tabbar layout, aligned to the dotnet capture
type: story
status: resolved
priority: medium
created: 2026-10-19
resolved: 2026-10-19
area: ui
parent: LP-0004
tags:
  - design-system
  - artifact
  - color
---

# Three color variants on the dense-tabbar layout, aligned to the dotnet capture

## Description

`LP-0004-05` picked the `dense-tabbar` layout, but its colors read gray, not
like the dotnet.microsoft.com example the user chose. Three color variants
on that fixed layout, all drawn from the existing capture, let the user pick
the palette by looking.

## Details

- Current: `.claude/skills/neta-design/tokens/dense-tabbar.css` uses only
  the capture's neutrals: an `rgb(245, 245, 245)` ground, white panels with
  1px `rgb(229, 231, 235)` hairlines, and no shadow. Purple
  `rgb(81, 43, 212)` appears only on buttons, the active tab, the progress
  fill, and links. Captured color it leaves unused: the deep accent
  `rgb(25, 6, 73)`, the stronger accent tint `rgb(220, 213, 246)`, the
  card hues magenta, blue, and flamingo, and the 2px colored card border.
- Desired: three variants in `artifacts/LP-0004-06-color-variants/`, built
  with `neta-design`:
  - **Values files.** One per variant at
    `.claude/skills/neta-design/tokens/<variant>.css`. Each starts from
    `dense-tabbar.css` and changes only the `--color-*` roles,
    `--border-width`, and new `--d-` color tokens. A color role that a
    second variant would also name extends `_structure.css`, as
    `tokens/README.md` says.
  - **Screens.** The same four pages as `LP-0004-05`: the dashboard, the
    quiz question, the graded quiz, and law detail. That makes 12 pages and
    36 shots, with the `dense-tabbar` markup and layout unchanged.
  - **Proposed variants**, each a different answer to "where does the color
    live". Names and theses are signed off before any HTML:
    - `purple-line`: one hue, as lines. Panels and options take 2px accent
      borders, as on the capture's `a.card.purple-primary`. Headings and
      metric numerals use the deep accent, on an `rgb(250, 250, 250)`
      ground.
    - `role-hues`: four hues, by fixed role. Purple, magenta, blue, and
      flamingo are each tied to one meaning on every screen. For example,
      選擇題 is always purple, 簡答題 always magenta, and each progress
      number has its own hue.
    - `purple-tint`: one hue, as surfaces. The accent tints fill the shell,
      the metric strip, and the start block, like the capture's announcement
      banner. Borders stay light.
- Not open, so every variant respects these:
  - The layout (top bar, bottom tab bar, desktop sidebar, page order),
    spacing, type sizes and weights, elevation, and motion of
    `LP-0004-05`'s `dense-tabbar`, per its `DECISION.md`. The less-AI pass
    in Settled Decisions reopened three other things: the panel treatment,
    the metric strip's form, and the emoji section markers.
  - All text is 黑體, the system sans stack in `--font-body`. No Ming face
    appears anywhere (user, 2026-10-19).
  - Every color comes from `docs/references/dotnet-microsoft-com/tokens.md`
    or is marked `derived:` with its reason.
  - The capture's do-not-reproduce list holds. No gradient, gradient text,
    radial wash, or per-card hue rotation appears. A hue is fixed to a role
    and never cycles from card to card.
  - Status colors stay semantic. Success, danger, warning, and info are
    never replaced by a role hue.
  - Light mode only. Mobile-first, with only the `min-width: 768px` and
    `1024px` breakpoints.
- Artifact required: the whole story is a palette the user picks by
  looking.
- No PRD: artifacts only. Nothing in `templates/`, `static/`, or the Python
  code changes.
- Out of scope: layout, spacing, or type-size changes. Also dark mode,
  adoption into `static/css/` and `templates/` (`LP-0004-07`), new copy
  beyond dropping the emoji section markers, and new pages.

## Acceptance Criteria

- [x] Three theses, one sentence each saying where the color lives, are
      signed off by the user before any HTML is written. See Settled
      Decisions.
- [x] Each variant's values file defines every `_structure.css` name. It
      differs from `dense-tabbar.css` only in `--color-*` roles,
      `--border-width`, and `--d-` tokens, with a source comment on every
      changed value.
- [x] Contrast holds: the contract's stated ratios, plus 4.5:1 for any hue
      used as text and 3:1 for any hue used as a border or fill (WCAG
      1.4.11). The `role-hues` flags are graphics: flamingo 3.35:1 on
      surface and 3.07:1 on bg, and blue 4.18:1 on bg. The white label on
      magenta is 4.73:1. `purple-tint`'s two accent tints are surfaces, not hues: they
      sit about 1.1:1 on the ground, as `--color-accent-surface` already
      does, and the text on them is what is checked. Muted text stays off
      the stronger tint, where it would be 4.39:1.
- [x] Each variant renders the four pages with the `dense-tabbar` layout and
      every shell control and label. Stand-in data is marked
      `<!-- stand-in -->`. The three variants share one body markup and
      differ only in `<head>`.
- [x] No gradient, gradient text, radial wash, or per-card hue rotation
      appears. In `role-hues`, each hue maps to one role on every page.
- [x] The `neta-design` hex grep prints nothing for
      `artifacts/LP-0004-06-color-variants/`.
- [x] Every page passes the `neta-design` verify at all three viewports: no
      console errors, tokens resolved, no page scroll, and no overflowing
      element. 36/36 with the cache disabled, after the less-AI pass, with
      no ledger label wrapping and every element on the sans stack.
- [x] Variants in `artifacts/LP-0004-06-color-variants/` screenshot at phone
      (390x844), tablet (768x1024), and desktop (1440x900), reviewed with
      the user; choice recorded in `DECISION.md`.
- [x] `DECISION.md` names the winning values file, or the blend and where
      each part came from, with the user as decider and the shots they
      looked at as evidence.
- [x] ~~`LP-0004-07` (adoption) is filed with `ticket-system`, scoped to
      the `LP-0004-05` layout and this story's palette.~~ Rewritten: the
      user asked for main colors other than purple to be compared first.
      That story is `LP-0004-08`, filed instead, and it carries the box for
      filing `LP-0004-07`. Adoption takes the palette `LP-0004-08` picks.
- [x] `pytest` green: artifacts only, so no new test. The box stays to
      confirm nothing regressed.
- [x] `flake8` clean.
- [x] Seen working: none in the app, since it does not change. Every page
      is checked in Playwright over `http.server`, as `neta-design`'s
      Verify step says.
- [x] Docs synced: a changelog entry. `docs/modules/ui/index.md` takes the
      decision in `LP-0004-07`, when the app's look actually changes.

## Open Questions

- None.

## Related Files

- `.claude/skills/neta-design/SKILL.md`
- `.claude/skills/neta-design/tokens/_structure.css`
- `.claude/skills/neta-design/tokens/README.md`
- `.claude/skills/neta-design/tokens/dense-tabbar.css`
- `docs/references/dotnet-microsoft-com/tokens.md`
- `docs/references/dotnet-microsoft-com/spec.md`
- `artifacts/LP-0004-05-design-directions/DECISION.md`
- `artifacts/LP-0004-05-design-directions/dense-tabbar-layout.css`
- `artifacts/LP-0004-05-design-directions/system.css`
- `artifacts/LP-0004-06-color-variants/`

## Handoff Appendix

### Settled Decisions

Confirmed with the user on 2026-10-19:

- "The Microsoft example" is the existing dotnet.microsoft.com capture from
  `LP-0004-04`. No new capture is needed.
- The layout is `dense-tabbar`'s and is not open.
- Variants change color roles and line weight only. Type, spacing, radius,
  and layout stay.
- The capture's four card hues may appear, but only fixed to roles. Rotation
  and gradients stay out, with the rest of the do-not-reproduce list.

Signed off by the user on 2026-10-19, before any HTML:

- **`purple-line`**: every panel and quiz option is outlined 2px in purple
  `rgb(81, 43, 212)`. Headings and metric numerals are set in the deep
  accent `rgb(25, 6, 73)`, on an `rgb(250, 250, 250)` ground with white
  surfaces.
- **`role-hues`**: purple, magenta, blue, and flamingo are each pinned to one
  meaning on every screen, so a hue tells the learner what kind of thing
  they are looking at. Panels stay white with light lines. The role map:
  - purple: actions, links, the active tab, the progress fill, 選擇題, and
    作答題數.
  - magenta: 簡答題, both the badge and its filter tab.
  - blue: 法條, meaning the 第 N 條 heading, paragraph numbers, and
    覆蓋法條數.
  - flamingo: 連續練習天數, with a `derived:` darker value for text.
  - neutral: 掌握題數 and 平均得分率. Status marks ✓ ✗ ☆ stay green, red,
    and amber.
- **`purple-tint`**: the shell, the metric strip, and the start block sit on
  the capture's accent tints, like its announcement banner. Borders stay
  light gray.

Less-AI pass, reopened by the user on 2026-10-19 after the first review.
The user asked for the three designs to read less AI-generated, and allowed
four settled decisions to reopen. The `dense-tabbar` layout stays.

- **Panel treatment.** Blocks are no longer all the same rounded card. Each
  role gets its own container:
  - A **ledger** (rules only): the progress numbers and the tips.
  - A **panel**: the working object, meaning the question, the graded
    result, and the related-questions list.
  - A **sheet**: the law article, square-cornered like a printed page.
  The filter tabs become index tabs on a rule instead of pills. The active
  phone tab is marked on its top edge instead of a filled pill.
- **Metric strip form.** The five numbers still come first. On phone they
  form a ruled list, with the label on the left and the number on the
  right. From 768px they form one ruled row, with each label and number on
  a shared baseline. They are no longer big-number tiles.
- **Emoji section markers.** 💡 學習小提示, 📝 相關題目, 💡 AI 解析（重點）,
  and the 📊 in the law meta line drop their emoji. This is proposed copy
  for `LP-0004-07`. Emoji on controls, such as 📢, ☆, and 💡 查看解析,
  stay.
- **Law text face, reopened and then returned.** A system Ming face for
  law text was tried, then the user asked for 黑體 throughout, with no Ming
  anywhere. Law text stays UI, as `LP-0004-05` decided. Only its container
  changed, to the sheet.
- **`role-hues` refined.** The hues are solid flag marks: badges, the
  ledger's flag keys, and a sticky flag on the law sheet. Text stays ink,
  except the purple actions and links. The captured magenta, blue, and
  flamingo are used as-is, so the derived darker text values are dropped.
- **`purple-line` refined.** Panels, the law sheet, and quiz options keep
  the 2px purple outline (`--d-outline-width`). Every 1px rule becomes the
  stronger accent tint, so all lines are one hue family, and
  `--border-width` goes back to 1px.

### Behavior Details

- File names: `<variant>-dashboard.html`, `<variant>-quiz.html`,
  `<variant>-quiz-result.html`, and `<variant>-law.html`, each shot to
  `shots/<variant>-<page>-{phone,tablet,desktop}.png`.
- Copy `LP-0004-05`'s `system.css` and `dense-tabbar-layout.css` into the
  new folder first, so neither artifact folder links the other. Both copies
  are shared by all three variants. A rule that only one variant needs,
  such as `role-hues`' per-metric hue, goes in that variant's own
  stylesheet, never in the shared copies.
- Captured color to draw on, with its `tokens.md` source:

  | Value | Role in the capture | Element |
  | --- | --- | --- |
  | `rgb(25, 6, 73)` | Hero heading, deep accent | `h1.display-2.title` |
  | `rgb(238, 234, 251)` | Accent tint | `a.btn.btn-default` on hover |
  | `rgb(220, 213, 246)` | Accent tint, stronger | `div.alert-promo.alert` |
  | `rgb(81, 43, 212)` | Card border, purple | `a.card.purple-primary` |
  | `rgb(214, 0, 170)` | Card border, magenta | `a.card.magenta-primary` |
  | `rgb(11, 108, 255)` | Card border, blue | `a.card.blue-primary` |
  | `rgb(246, 81, 99)` | Card border, flamingo | `a.card.flamingo-primary` |
  | `2px solid` | Card border weight | `a.card.purple-primary` |

- Contrast pre-check on white: magenta reaches 4.73:1 and blue 4.56:1, so
  both pass as text, barely. Flamingo reaches 3.35:1, so it passes only as
  a border or fill and needs a `derived:` darker value for text. Blue text
  on a tint will likely fail 4.5:1.
- Build order: one variant first, verified, then the other two, as in
  `LP-0004-05`.
- Verify with the browser cache disabled. `http.server` sends
  `Last-Modified`, and Chromium then reuses stale stylesheets across
  rebuilds. `LP-0004-05` saw a fixed overflow still fail until the cache
  was off.

### Deferred Decisions

- Adoption is `LP-0004-07`: the values file in `static/css/`, `style.css`
  and `templates/` on contract names, and the MUI CDN dropped. It also
  covers progress data on `/`, which the dashboard's metric strip needs.
  See the carry-forward in `LP-0004-05`'s `DECISION.md`.

## Resolution

Three palettes landed on the `dense-tabbar` layout, reworked in a less-AI
pass with all text in 黑體, and the user picked `role-hues`
([`DECISION.md`](../../../../artifacts/LP-0004-06-color-variants/DECISION.md)).
Its main color was deliberately not settled: `LP-0004-08` compares purple
with blue and a derived teal, and adoption (`LP-0004-07`) is filed after
that. See [the changelog entry](../../../changelog/2026-10-19-color-variants.md).
