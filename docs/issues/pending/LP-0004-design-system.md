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
  - `LP-0004-04` Capture `dotnet.microsoft.com` (home and `/en-us/learn`)
    with `site-capture` (`docs`).
  - `LP-0004-05` Three design-system directions from that capture on the
    dashboard, quiz session, and law detail screens. The user picks and
    iterates. Artifact required (`ui`). The user picked the `dense-tabbar`
    layout. Color went to `LP-0004-06`.
  - `LP-0004-06` Three color variants on the `dense-tabbar` layout, drawn
    from the same capture. The user picks the palette. Artifact required
    (`ui`). The user picked `role-hues`. Its main color went to
    `LP-0004-08`.
  - `LP-0004-07` Adopt the picked layout and palette: its values file replaces both
    Figma token files in `static/css/`, `style.css` and `templates/`
    migrate onto the contract names, and the MUI CDN is dropped. One
    story, filed once `LP-0004-08`'s `DECISION.md` lands, because its
    scope depends on the pick. Filed, covering every page, with a PRD. The PRD call is made then: `/` must also
    load the progress numbers the `dense-tabbar` dashboard opens on.
  - `LP-0004-08` Compare `role-hues` with blue and with a derived teal as its
    main color, against the purple baseline. The user picks. Artifact
    required (`ui`). The user picked teal.
  - `LP-0004-09` Dark mode on the adopted tokens, with each learner's
    choice stored in a new `user_ui_flags` collection. Artifact and PRD
    required (`ui`).
- Order: `01` → `02` → `04` → `05` → `06` → `08` → `07` → `09`. `02`'s token section reads the
  output format `01` defines. `03` depends on nothing and lands before `07`,
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

Confirmed with the user on 2026-10-18:

- The reference site is `https://dotnet.microsoft.com/en-us/`, recorded
  without the `?utm_source=tailwindcss` referral tag. The slug is
  `dotnet-microsoft-com`, and the capture covers the homepage and
  `/en-us/learn` only.
- The .NET accent purple is a token, taken from the capture like every
  other value, and not a branded motif.
- Directions: three, applied to the dashboard, quiz session, and law
  detail screens. One keeps today's layout as the baseline. All four layout
  axes are open: phone navigation, density, dashboard entry point, and law
  text treatment.
- Adoption retires `design-tokens.css` and `design-tokens-dark.css`. Nobody
  regenerates them from Figma.
- Adoption drops the MUI 0.10.3 CDN from `base.html`. No template or script
  uses a `mui-` class, so it supplies only a global reset.

Confirmed with the user on 2026-10-19:

- The `dense-tabbar` layout wins `LP-0004-05`. Its colors read gray, not
  like the example, so color is a separate story, `LP-0004-06`. Adoption
  becomes `LP-0004-07`.
- The color variants draw only from the dotnet capture. They change color
  roles and line weight, not type, spacing, radius, or layout. The capture's
  four card hues may appear fixed to roles, never rotating, and gradients
  stay out.
- After the first `LP-0004-06` review, the user asked for a less-AI pass.
  It reopened the panel treatment, the metric strip's form, and the emoji
  section markers. All text is 黑體, with no Ming face anywhere.
- `role-hues` wins `LP-0004-06`. Before adoption, `LP-0004-08` compares its
  main color, purple, with the capture's blue and a teal. The teal is the
  one value allowed from outside the dotnet capture, marked `derived:` with
  its reason. Adoption follows `LP-0004-08`.
- Teal wins `LP-0004-08`. `LP-0004-07` adopts the teal `role-hues` palette on
  every page in one story, and the dashboard's five numbers cover all time.

Confirmed with the user on 2026-10-20:

- Dark mode joins the epic as `LP-0004-09`. It offers light and dark only,
  with light as the default, and derives its dark values from the light
  tokens. The choice is stored per user in `user_ui_flags`.

- No artifact at the epic level. `LP-0004-05` and `LP-0004-06` carry the
  visual choices.
- Out of scope: copying any reference asset, copy, logo, or branded motif;
  new pages or routes beyond `LP-0004-09`'s save route; UI copy changes
  beyond `LP-0004-09`'s toggle label.

## Acceptance Criteria

- [ ] All child stories are `resolved` or `wont_fix`.
- [ ] `CLAUDE.md` names `site-capture` and `neta-design` where the workflow
      invokes them. `design-variants` appears only in changelog entries and
      `LP-0001` tickets.
- [ ] Every page passes the three-viewport check: no page scroll and no
      overflowing element. `LP-0004-03` sets this and `LP-0004-07` keeps it.
- [ ] `pytest` green: covered by the child stories.
- [ ] `flake8` clean: covered by the child stories.
- [ ] Seen working: covered by each child story.
- [ ] Docs synced: covered by the child stories' changelog entries and
      `docs/modules/ui/index.md`.

## Open Questions

- None.

## Related Files

- `CLAUDE.md`
- `.claude/skills/design-variants/`
- `.claude/skills/site-capture/`
- `.claude/skills/neta-design/`
- `static/css/design-tokens.css`
- `static/css/design-tokens-dark.css`
- `static/css/style.css`
- `templates/`
- `docs/references/dotnet-microsoft-com/`
- `artifacts/LP-0004-05-design-directions/`
- `artifacts/LP-0004-06-color-variants/`
- `artifacts/LP-0004-08-main-color/`
- `artifacts/LP-0004-09-dark-mode/`
- `docs/issues/*/LP-0004-design-system/`
