---
id: LP-0004
title: Design system from captured reference sites, with RWD on every page
type: epic
status: pending
priority: medium
created: 2026-10-17
resolved:
area: ui
tags:
  - design-system
  - rwd
  - skills
---

# Design system from captured reference sites, with RWD on every page

## Description

The app's look comes from Figma-generated token files that nobody here can
regenerate, and its layout was only ever checked at phone and desktop. This
epic brings in the neta-homepage design workflow: capture a reference site,
derive a design system from it, let the user pick by looking, and adopt it,
with every page holding at phone, tablet, and desktop.

## Details

- Current:
  - `static/css/design-tokens.css` and `design-tokens-dark.css` say
    `自動生成自 Figma 設計系統` / `請勿手動編輯此檔案`, but no generator lives
    in the repo.
  - `static/css/style.css` (2,251 lines) mixes four breakpoint styles:
    `max-width: 640px`, `max-width: 767px`, `min-width: 768px`, and
    `min-width: 1024px`. Six templates carry inline `style=` attributes, 31
    of them in `law_detail.html`.
  - `design-variants` builds per-ticket variants against the Figma tokens,
    at phone 390x844 and desktop 1440x900 only. `LP-0001` left "a
    design-token or design-system skill" out of scope. This epic picks it up.
- Desired: the workflow of `/Users/johnnychang/moblab/neta-homepage/`,
  adapted to this repo:
  - `site-capture` reads an **external reference site** into a written spec
    with measured tokens. It never captures law_pass itself.
  - `neta-design` turns a capture into a token contract and design
    artifacts the user picks from. It is built from `design-variants`'
    content with neta's additions merged in, and it replaces
    `design-variants`.
  - Every page holds at phone 390x844, tablet 768x1024, and desktop
    1440x900.
- Roadmap:
  - `LP-0004-01` `site-capture` skill (`docs`).
  - `LP-0004-02` `neta-design` skill, merged from `design-variants` (`ui`).
  - `LP-0004-03` RWD pass: every page holds at all three viewports on the
    current CSS (`ui`).
  - `LP-0004-04` Capture the first reference site(s) with `site-capture`.
    Filed once the reference URLs are named.
  - `LP-0004-05` Design-system directions: `neta-design` builds two or three
    directions from the captures on real law_pass screens, and the user
    picks. Artifact required.
  - `LP-0004-06` Adopt the chosen design system: its tokens replace the
    Figma files in `static/css/`, and `style.css` and `templates/` migrate
    onto it. The PRD call is made when it is filed.
- Order: `01` → `02` → `04` → `05` → `06`. `02`'s token section reads the
  output format `01` defines. `03` depends on nothing and lands before `06`,
  so adoption starts from a layout that already holds and only has to keep
  it holding.

### Settled Decisions

Confirmed with the user on 2026-10-17:

- `site-capture` captures external reference sites, not our own app.
- The design system's tokens come from the site capture.
- `neta-design` starts from our `design-variants` skill content, merges the
  neta-homepage `neta-design` additions in, and replaces `design-variants`.
  The skill keeps the name `neta-design`.
- "Fine on all devices" means phone 390x844, tablet 768x1024, and desktop
  1440x900. The tablet viewport joins the artifact contract and the done
  gate.

- No artifact at the epic level. `LP-0004-05` carries the visual choice.
- Out of scope: copying any reference asset, copy, logo, or branded motif;
  dark mode (`design-tokens-dark.css` is not wired today); new pages or
  routes; UI copy changes.

## Acceptance Criteria

- [ ] All child stories are `resolved` or `wont_fix`.
- [ ] `CLAUDE.md` names `site-capture` and `neta-design` where the workflow
      invokes them. `design-variants` appears only in changelog entries and
      `LP-0001` tickets.
- [ ] Every page passes the three-viewport check: no page scroll and no
      overflowing element. `LP-0004-03` sets this and `LP-0004-06` keeps it.
- [ ] `pytest` green: covered by the child stories.
- [ ] `flake8` clean: covered by the child stories.
- [ ] Seen working: covered by each child story.
- [ ] Docs synced: covered by the child stories' changelog entries and
      `docs/modules/ui/index.md`.

## Open Questions

- Which reference site(s) does the design system draw from? This blocks
  filing `LP-0004-04`. It does not block `01`–`03`.

## Related Files

- `CLAUDE.md`
- `.claude/skills/design-variants/`
- `.claude/skills/site-capture/`
- `.claude/skills/neta-design/`
- `static/css/design-tokens.css`
- `static/css/design-tokens-dark.css`
- `static/css/style.css`
- `templates/`
- `docs/issues/*/LP-0004-design-system/`

## Handoff Appendix

### Deferred Decisions

- Whether anyone still regenerates `design-tokens*.css` from Figma. Decided
  when `LP-0004-06` is filed, since that story retires the Figma files.
- Whether adoption drops the MUI CDN (`mui-0.10.3`, loaded in `base.html`).
  Decided when `LP-0004-06` is filed.
