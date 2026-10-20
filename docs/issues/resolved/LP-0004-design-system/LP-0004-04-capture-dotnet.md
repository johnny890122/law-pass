---
id: LP-0004-04
title: Capture dotnet.microsoft.com as the design system's reference site
type: story
status: resolved
priority: medium
created: 2026-10-18
resolved: 2026-10-18
area: docs
parent: LP-0004
tags:
  - design-system
  - reference-capture
---

# Capture dotnet.microsoft.com as the design system's reference site

## Description

`LP-0004-05` derives law_pass's design-system directions from one reference
site, and the user picked `dotnet.microsoft.com`. This story records it
with `site-capture`, so that no later step has to reopen the live site.

## Details

- Current: `docs/references/` does not exist, and no reference site has
  been captured.
- Desired: `docs/references/dotnet-microsoft-com/`, written by following
  `site-capture`:
  - Pages: `https://dotnet.microsoft.com/en-us/` (shot as `home`) and
    `https://dotnet.microsoft.com/en-us/learn` (shot as `learn`). No
    crawling, and no other page.
  - `spec.md`, `tokens.md`, and six shots:
    `shots/{home,learn}-{phone,tablet,desktop}.png` at 390x844, 768x1024,
    and 1440x900.
  - Capture the site's default light theme. The site has a theme toggle.
    Record it in the interaction inventory, but do not capture the dark
    theme, because dark mode is out of scope for `LP-0004`.
  - Record the .NET accent purple in `tokens.md` as a color role. It is a
    token, not a branded motif, so it stays off the do-not-reproduce list.
    The .NET logo, wordmark, mascot, illustrations, and copy stay on it.
- The skill's confirm step is already answered by the URLs and scope
  above. Restate them at the start of the capture rather than asking again.
- No artifact — this records an external site, and no law_pass screen
  changes.
- No PRD — a docs-only skill run.
- Out of scope: capturing law_pass, any page beyond the two above, the
  dark theme, downloading assets, and proposing tokens (that is
  `LP-0004-05`).

## Acceptance Criteria

- [x] `docs/references/dotnet-microsoft-com/` holds only `spec.md`,
      `tokens.md`, and the six `shots/`, and both files carry the dated
      header with the two-page scope.
- [x] Every `tokens.md` row names an element and a viewport, and the
      .NET accent appears as a color role (`rgb(81, 43, 212)`, plus its
      hover and two tints).
- [x] Neither file quotes the site's copy, and `spec.md`'s
      do-not-reproduce list names the site's logo, wordmark, mascot,
      illustrations, and copy. A grep for the site's headlines and labels
      finds none.
- [x] The skill's output check passes: read cold, the folder is enough to
      build each section at all three viewports. `spec.md` §4 gives every
      section a layout at 390, 768, and 1440.
- [x] `pytest` green: no code or test change. The box stays to confirm
      nothing regressed. 101 passed.
- [x] `flake8` clean.
- [x] Seen working: none — the capture changes no app behavior. The output
      check above stands in.
- [x] Docs synced: a changelog entry. No module doc applies, because no
      product rule changes.

## Open Questions

- None.

## Related Files

- `.claude/skills/site-capture/SKILL.md`
- `docs/references/dotnet-microsoft-com/`

## Resolution

Captured dotnet.microsoft.com's homepage and learning hub into
`docs/references/dotnet-microsoft-com/`, with six full-page shots, the .NET
accent recorded as a token, and observed breakpoints at 540, 845, 860, and
1248px. The Playwright MCP browser was locked, so a local script ran the
skill's snippet, with a supplement pass for borders, gradients, states, and
a width sweep. The skill itself was not extended. See
[2026-10-18-dotnet-capture](../../../changelog/2026-10-18-dotnet-capture.md).
