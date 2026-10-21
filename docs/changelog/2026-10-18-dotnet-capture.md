# 2026-10-18 — dotnet.microsoft.com captured as the design system's reference

**LP ids:** LP-0004-04

law_pass's first real reference site is on file. Following
[`site-capture`](../../.claude/skills/site-capture/SKILL.md), the homepage
and learning hub of dotnet.microsoft.com were measured at 390x844,
768x1024, and 1440x900 into
[`docs/references/dotnet-microsoft-com/`](../references/dotnet-microsoft-com/).
`LP-0004-05` derives its three design-system directions from this folder
alone. No product behavior changed, so no module doc applies.

| Area | Was | Now |
| --- | --- | --- |
| Reference captures | `docs/references/` did not exist. | `dotnet-microsoft-com/` holds `spec.md`, `tokens.md`, and six full-page shots (`home` and `learn` × phone, tablet, desktop). |
| Accent source | The Figma purple, `#8d1ff4`. | The capture records the site's accent, `rgb(81, 43, 212)`, with its hover `rgb(65, 34, 170)` and two tints, as a color role. Per `LP-0004` it is a token, not a motif. |
| Layout evidence | — | Observed breakpoints are 540, 845, 860 (header), and 1248px. Content grids run 1 → 2 → 4 columns, with no horizontal page scroll at any viewport. |
| Do-not-reproduce | — | Logos, mascots, illustrations, the presenter photo, gauge art, third-party and social logos, icon sets, font files, the gradient-text, gradient-band, radial-wash, and hue-rotation motifs, and all copy. |

How it was measured:

- The Playwright MCP browser profile was held by another session, so a
  local script drove the same Playwright build (1.62.1, Chromium 1234). It
  ran the skill's measure snippet verbatim, as `LP-0004-01`'s smoke did.
- The snippet tallies no border colors, background gradients, text fill, or
  interaction states. A second computed-style pass read those, plus a 4px
  width sweep for breakpoints, because the parent-brand stylesheet is
  cross-origin. `tokens.md` marks those rows "supplement". No value was
  read off a screenshot.

## Deliberately not done

- No dark theme. The site has a theme toggle, but dark mode is out of scope
  for `LP-0004`.
- No page beyond the two in scope, and no link was followed to find more.
- No token was proposed or mapped onto `_structure.css`. That is
  `LP-0004-05`.
- The `site-capture` snippet was not extended with the supplement's
  reads. The scripts lived in the session scratchpad and are not committed.
  Changing the skill needs its own ticket.
- The site renders no success, danger, or warning color, so the capture
  records none. `LP-0004-05` derives those roles in the open.
