---
id: LP-0004-05
title: Three design-system directions from the dotnet capture, picked by looking
type: story
status: resolved
priority: medium
created: 2026-10-18
resolved: 2026-10-19
area: ui
parent: LP-0004
tags:
  - design-system
  - artifact
---

# Three design-system directions from the dotnet capture, picked by looking

## Description

There is no designer, so the user picks law_pass's next design system by
looking at it on real screens. `neta-design` turns the `LP-0004-04` capture
of `dotnet.microsoft.com` into three directions, and the user iterates on
them until one wins.

## Details

- Current: the app's look comes from the Figma token files, and
  `.claude/skills/neta-design/tokens/` holds only the `_structure.css`
  contract with placeholder values.
- Desired: three directions in `artifacts/LP-0004-05-design-directions/`,
  built by following `neta-design`'s design-system-directions path:
  - **Theses first.** One sentence per direction, committing to a layout,
    signed off by the user before any HTML. One direction is the
    **baseline**: today's layout on the dotnet tokens. The other two commit
    to different positions on the open axes below.
  - **Values files.** One per direction, at
    `.claude/skills/neta-design/tokens/<direction>.css`, named by its
    thesis. Each defines every `_structure.css` name. Every value cites
    `docs/references/dotnet-microsoft-com/tokens.md` or is marked
    `derived:` with its reason. A role the contract lacks extends the
    contract, as `tokens/README.md` says.
  - **Screens.** Each direction renders four pages: the dashboard, the
    quiz session in its question state, the quiz session in its graded
    state (`quiz_session.html` swaps the question card for
    `#result-card`), and law detail. That makes 12 pages, and 36 shots at
    three viewports.
  - **Build order.** The baseline is built and verified first, which proves
    the system/direction split. The two bolder directions follow.
  - **Iterate.** The user reviews the shots, phone first, and revisions run
    in rounds until the user picks. Earlier decisions hold unless the user
    reopens them. Pages are re-shot after every revision. A blend is a
    valid winner if it says which part came from which direction.
- Open axes, which directions may vary on: phone navigation (top nav,
  bottom tab bar, or desktop sidebar), density, dashboard entry point
  (stats, next quiz, or law browsing first), and law text treatment (as UI
  or set apart as a document).
- Not open, so every direction respects these:
  - The `base.html` shell controls and labels, as `neta-design`'s Ground
    step lists them. A direction may restyle or rearrange them, but keeps
    every one.
  - The accent comes from the capture: the .NET purple is a token.
  - Light mode only. Mobile-first, with only the `min-width: 768px` and
    `1024px` breakpoints.
  - Real UI copy is quoted from `templates/` and `static/js/`. Law text
    comes from `knowledge/` or is marked stand-in. Nothing from the
    capture's do-not-reproduce list appears.
- Artifact required — the whole story is a choice the user makes by
  looking.
- No PRD — artifacts only. Nothing in `templates/`, `static/`, or the
  Python code changes.
- Out of scope: editing `static/css/` or `templates/` (adoption, now
  `LP-0004-07`), dark mode, screens beyond the four above, new copy, and
  new routes.

## Acceptance Criteria

- [x] Three theses, one of them the baseline, are signed off by the user
      before any HTML is written. Each thesis becomes its direction's
      decision label.
- [x] Each direction's values file defines every `_structure.css` name,
      with a source comment on every value, and meets the contrast ratios
      the contract states.
- [x] Each direction renders the four pages and keeps every shell control
      and label. Stand-in data is marked `<!-- stand-in -->`.
- [x] The `neta-design` hex grep prints nothing for
      `artifacts/LP-0004-05-design-directions/`.
- [x] Every page passes the `neta-design` verify at all three viewports: no
      console errors, tokens resolved, no page scroll, and no overflowing
      element.
- [x] Variants in `artifacts/LP-0004-05-design-directions/` screenshot at
      phone (390x844), tablet (768x1024), and desktop (1440x900), reviewed
      with the user; choice recorded in `DECISION.md`.
- [x] `DECISION.md` names the winning values file, or the blend and where
      each part came from, with the user as decider and the shots they
      looked at as evidence. Note: the winner is `dense-tabbar`'s layout
      and its non-color values. Its `--color-*` roles and `--border-width`
      are reopened by `LP-0004-06`, at the user's request.
- [x] `LP-0004-06` is filed with `ticket-system`, scoped to the winner.
      Note: at the user's request it is three color variants on the
      `dense-tabbar` layout. Adoption moved to `LP-0004-07`, filed once
      `LP-0004-06` picks.
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
- `docs/references/dotnet-microsoft-com/`
- `artifacts/LP-0004-05-design-directions/`
- `templates/base.html`
- `templates/dashboard.html`
- `templates/quiz_session.html`
- `templates/law_detail.html`

## Handoff Appendix

### Settled Decisions

Confirmed with the user on 2026-10-18:

- Three directions: a baseline plus two bolder ones.
- Four pages per direction, covering the dashboard, both quiz session
  states, and law detail.
- All four layout axes are open.
- The .NET accent purple is taken as a token.

Confirmed with the user on 2026-10-19:

- Type stays on system stacks. The capture supplies sizes, weights, and
  line heights, but not its `Space Grotesk` and `Open Sans` faces. The
  contract's "System stacks only" rule holds, and no direction adds a font
  request.
- The three theses, signed off as written, are the decision labels:
  - `baseline`: today's layout with the dotnet values. The top nav still
    wraps to two rows on phone, the dashboard still opens on `開始新測驗`
    with `法條瀏覽` and `我的題目` under it, and law text stays inside the
    card as UI.
  - `dense-tabbar`: a study app. On phone a bottom tab bar holds the four
    nav links and a one-row top bar holds the law-type select, `中`/`EN`,
    and the user menu. On desktop the nav becomes a left sidebar. The
    dashboard opens on the five progress numbers from `progress.html` in a
    tight strip with `開始新測驗` under it. Dense enough that a whole
    question and its options fit one phone screen.
  - `reading-room`: a quiet reading room. A one-row top bar and generous
    whitespace. The dashboard opens on law browsing: `開始新測驗` leads,
    then the current law's chapters as bordered cards. Law text and
    question stems are set apart as a document, with a narrow measure, a
    sunken page-like panel, a distinct law face, and wide leading.

### Behavior Details

- File names follow the contract, `<variant>` being the file stem:
  `<direction>-dashboard.html`, `<direction>-quiz.html`,
  `<direction>-quiz-result.html`, and `<direction>-law.html`, each shot to
  `shots/<direction>-<page>-{phone,tablet,desktop}.png`.
- The folder shares one `system.css` across directions. A direction that
  needs a system-tier edit means the boundary is wrong, so fix the
  boundary rather than special-casing the direction.
- Depends on `LP-0004-04`: no values file is written before
  `docs/references/dotnet-microsoft-com/tokens.md` exists.

## Resolution

Three directions landed, each with a cited values file and four pages at
three viewports, and the user picked the `dense-tabbar` layout
([`DECISION.md`](../../../../artifacts/LP-0004-05-design-directions/DECISION.md)).
The palette was deliberately not picked: it goes to `LP-0004-06`, and
adoption moves to `LP-0004-07`. See
[the changelog entry](../../../changelog/2026-10-19-design-directions.md).
