---
id: LP-0004-08
title: Compare blue and teal against purple as role-hues' main color
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

# Compare blue and teal against purple as role-hues' main color

## Description

The user picked `role-hues` in `LP-0004-06`. Before adoption locks it in,
they want to see it with a main color other than purple. The main color
reaches every screen, so it is a choice the user makes by looking.

## Details

- Current: in `.claude/skills/neta-design/tokens/role-hues.css`:
  - Purple `rgb(81, 43, 212)` is the main color. It fills
    `--color-accent` (buttons, the active tab, the progress fill),
    `--color-link`, `--color-data-1`, and, through `role-hues-color.css`,
    the 選擇題 and 作答題數 flags.
  - Its steps are captured: hover `rgb(65, 34, 170)` and surface
    `rgb(238, 234, 251)`.
  - The role flags are magenta (簡答題), blue (法條), and flamingo
    (連續練習天數).
- Desired: three variants in `artifacts/LP-0004-08-main-color/`, built with
  `neta-design`. Only the main color differs between them:
  - **`purple`**: `role-hues` as picked, the baseline. It reuses
    `role-hues.css` with no new values file.
  - **`blue`**: the main color is the capture's card blue
    `rgb(11, 108, 255)`. 法條 moves to purple, which the swap frees, so no
    hue carries two meanings. Values file `tokens/role-hues-blue.css`.
  - **`teal`**: the main color is a teal from outside the capture. 法條
    stays blue. Values file `tokens/role-hues-teal.css`.
  - The main color fills the whole accent family: `--color-accent`, its
    hover, contrast, and surface, `--color-link` and its hover,
    `--color-data-1`, and the 選擇題 and 作答題數 flags. A step the
    capture does not record for that hue is derived the way purple's
    captured steps relate.
  - **Screens.** The same four pages as `LP-0004-06`: the dashboard, the
    quiz question, the graded quiz, and law detail. That makes 12 pages and
    36 shots, with `LP-0004-06`'s final `role-hues` body markup and shared
    tiers unchanged.
- Not open, so every variant respects these:
  - Everything in `LP-0004-06`'s `DECISION.md` except the main color. That
    covers the layout, the ledger, panel, and sheet containers, the index
    tabs, hues as flags held to 3:1, text in ink, 黑體 only, and the role
    map, apart from 法條's move in `blue`.
  - Every color comes from `docs/references/dotnet-microsoft-com/tokens.md`
    or is marked `derived:` with its reason. The teal is the one value from
    outside the capture (user, 2026-10-19).
  - Status colors stay semantic. Success, danger, warning, and info are
    never replaced by the main color or a role hue.
  - No gradient, gradient text, radial wash, or per-card hue rotation.
    Light mode only. Mobile-first, with only the `min-width: 768px` and
    `1024px` breakpoints.
- Artifact required: the main color is a palette choice the user makes by
  looking.
- No PRD: artifacts only. Nothing in `templates/`, `static/`, or the Python
  code changes.
- Out of scope: adoption into `static/css/` and `templates/` (`LP-0004-07`),
  role-map changes beyond 法條's move in `blue`, and layout, type, spacing,
  or copy changes. Also dark mode and new pages.

## Acceptance Criteria

- [x] The teal value and the `blue` and `teal` theses, one sentence each,
      are signed off by the user before any HTML is written. See Settled
      Decisions.
- [x] `role-hues-blue.css` and `role-hues-teal.css` define every
      `_structure.css` name. Each differs from `role-hues.css` only in the
      accent family and the `--d-` flag tokens, with a source comment on
      every changed value.
- [x] Contrast holds in every variant:
      - the main color as text, at 4.5:1 on surface, on bg, and on its own
        surface;
      - a white label on the main fill, at 4.5:1;
      - every flag, at 3:1 on surface and on bg.
      A value that fails is replaced by a `derived:` one. `blue` uses the
      derived `#0061f5`: 4.78:1 on bg and 4.53:1 on its surface. Teal
      passes as-is: 5.22:1 on bg and 4.94:1 on its surface. Purple 法條 is
      7.28:1 on bg.
- [x] Each variant renders the four pages. The three share one body markup
      and differ only in `<head>`. Stand-in data is marked
      `<!-- stand-in -->`.
- [x] In every variant, each hue maps to one meaning on every page. No hue
      is both the main color and a role flag.
- [x] The `neta-design` hex grep prints nothing for
      `artifacts/LP-0004-08-main-color/`.
- [x] Every page passes the `neta-design` verify at all three viewports: no
      console errors, tokens resolved, no page scroll, and no overflowing
      element. 36/36 with the cache disabled. `LP-0004-06`'s `role-hues`
      pages still resolve every flag after the `--d-flag-*` rename.
- [x] Variants in `artifacts/LP-0004-08-main-color/` screenshot at phone
      (390x844), tablet (768x1024), and desktop (1440x900), reviewed with
      the user; choice recorded in `DECISION.md`.
- [x] `DECISION.md` names the winning values file, with the user as decider
      and the shots they looked at as evidence.
- [x] `LP-0004-07` (adoption) is filed with `ticket-system`. It is scoped
      to the `LP-0004-05` layout, `LP-0004-06`'s `role-hues` frame, and this
      story's main color. The user widened it to every page.
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
- `.claude/skills/neta-design/tokens/README.md`
- `.claude/skills/neta-design/tokens/role-hues.css`
- `docs/references/dotnet-microsoft-com/tokens.md`
- `artifacts/LP-0004-06-color-variants/DECISION.md`
- `artifacts/LP-0004-06-color-variants/role-hues-color.css`
- `artifacts/LP-0004-06-color-variants/system.css`
- `artifacts/LP-0004-06-color-variants/dense-tabbar-layout.css`
- `artifacts/LP-0004-08-main-color/`

## Handoff Appendix

### Settled Decisions

Confirmed with the user on 2026-10-19:

- `role-hues` is the `LP-0004-06` winner. This story changes only its main
  color.
- The candidates are blue from the capture and a teal from outside it,
  each compared against purple. The user chose this over a capture-only
  pair of blue and ink.
- Signed off before any HTML: the user answered the proposal with "please
  implement".
  - Teal `#00727a`.
  - **`blue`**: blue is the main color, and 法條 moves to purple.
  - **`teal`**: teal is the main color, and 法條 stays blue.
- Derived at build, per the contrast box:
  - **`blue`'s main color is `#0061f5`.** It is the captured
    `rgb(11, 108, 255)` darkened with its hue held, to the lightest value
    that passes 4.5:1 on the ground (4.78:1) and on its own tint (4.53:1).
    `--color-accent` is both fill and text in the system tier, so one value
    has to pass both.
  - **Hover** steps are the main color's lightness × 0.8, which is how the
    capture's purple hover relates to its purple.
  - **Surfaces** are the main color at 0.098 alpha over white, which is how
    the capture's purple tint relates to its purple.

### Behavior Details

- File names: `<variant>-<page>.html` for the variants `purple`, `blue`,
  and `teal`, and the pages `dashboard`, `quiz`, `quiz-result`, and `law`.
  Shots go to `shots/<variant>-<page>-{phone,tablet,desktop}.png`.
- Copy `LP-0004-06`'s `system.css`, `dense-tabbar-layout.css`,
  `role-hues-color.css`, and the `role-hues-*.html` body markup into the new
  folder, so neither folder links the other.
- **Name role tokens by meaning.** `role-hues-color.css` reads `--d-blue`
  for 法條. In `blue`, 法條 is purple, so a token named `--d-blue` would
  hold purple. Rename the flag tokens by meaning, such as `--d-flag-law`,
  `--d-flag-short`, and `--d-flag-streak`. Do it in `role-hues.css` too,
  so the baseline reads the same names. The token README already asks for
  semantic names.
- Proposed teal, for sign-off: `#00727a`, `rgb(0, 114, 122)`, at hue 184°.
  - It sits 37° from success green `#107c41` (147°) and 32° from info blue
    `#0a5bd6` (216°).
  - As text it reaches 5.69:1 on white and 5.22:1 on the `role-hues` ground
    `#f5f5f5`, and a white label on it reaches 5.69:1.
- Blue pre-check:
  - As text it reaches only 4.18:1 on `#f5f5f5`. Links and the progress
    count sit on the ground, so text needs a `derived:` darker blue, such
    as `#0064fd` at 4.54:1 on bg.
  - A white label on the blue fill reaches 4.56:1, which passes barely.
  - Blue on its own tint is about 4.0:1 and fails, so the active tab's text
    needs the darker blue too.
  - The main blue will sit close to info blue `#0a5bd6`, which is derived
    from the same capture blue. The review should name this.
- Build order: one variant first, verified, then the other, as in
  `LP-0004-06`. Verify with the browser cache disabled.

### Deferred Decisions

- Adoption is `LP-0004-07`, filed from this story's `DECISION.md`.

## Resolution

Teal `#00727a` won over purple and the capture's blue as `role-hues`' main
color ([`DECISION.md`](../../../../artifacts/LP-0004-08-main-color/DECISION.md)).
Its hover and tint are derived by the capture's purple steps, and the flag
tokens are now named by meaning. Adoption is filed as `LP-0004-07`. See
[the changelog entry](../../../changelog/2026-10-19-main-color.md).
