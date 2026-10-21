# LP-0004-09 · Decision

**Question:** what does the derived dark palette look like on the adopted
`dense-tabbar` and teal `role-hues` app?

## Winner: `teal-ink`

Values file: `.claude/skills/neta-design/tokens/dark-teal-ink.css`, an
overlay of `:root[data-theme="dark"]` on `static/css/tokens.css`.

The ground and panels carry a faint teal hue, like thinned teal ink on a
dark sheet. The ground is `#101a1b` and the panels `#172323`, one 1.10:1 step
up, the step light mode's white panels take over `#f5f5f5`. Text and the
other three role hues stay neutral in meaning.

## Rejected

- **`neutral`** (`dark-neutral.css`): a neutral near-black `#181818` with
  panels at `#212121`. It reads as the light app inverted. The user preferred
  the teal ground's mood.
- **`dim`** (`dark-dim.css`): a lighter `#242424` ground shared by the
  panels, which separate by lines at 1.7:1, with off-white text at 10.6:1
  for less glare. It gives up panel depth.

## What the real implementation must keep

- **The derivation rule.** Each role keeps its light hue at 0.6× saturation,
  so nothing glows. It is lightened until it has the same contrast on the dark
  panel that its light value has on white. A role with a tint is also
  lightened until it clears 4.5:1 on that tint, which moved only success.
- **Every value in `dark-teal-ink.css`**, copied into a
  `:root[data-theme="dark"]` block in `static/css/tokens.css` with its
  `derived:` comment and ratios, plus `color-scheme: dark`. It redefines
  only tokens whose value changes. Type, space, radius, layout, motion, and
  `--brand-*` stay light.
- **The contrast the ticket requires**, all on these values:

  | Role | Value | Contrast |
  | --- | --- | --- |
  | Text | `#ecf0f0` | 15.43:1 bg, 14.06:1 surface, 14.68:1 sunken |
  | Muted text | `#92a4a5` | 6.81:1 bg, 6.21:1 surface, 6.48:1 sunken |
  | Accent (teal) | `#2ca9b1` | 6.26:1 bg, 5.70:1 surface, 4.73:1 on its tint |
  | Label on accent | `#101a1b` (the ground) | 6.26:1 on accent, 8.63:1 on hover, 5.20:1 on the 簡答題 flag |
  | 簡答題 flag | `#d65dbe` | 5.20:1 bg, 4.74:1 surface |
  | 法條 flag | `#5789d5` | 5.01:1 bg, 4.57:1 surface |
  | Streak flag | `#c74353` | 3.67:1 bg, 3.35:1 surface |
  | Focus | `#ffffff` | 17.71:1 bg, 16.14:1 surface |

- **Labels on fills turn dark.** `--color-accent-contrast` becomes the
  ground, so filled buttons, the 選擇題 badge, and the 簡答題 badge carry a
  dark label on a light fill.
- **Danger stays rose** (`#d2949c`). The user kept it on the shared
  saturation rule rather than making it redder.
- **`--color-data-1` and `--color-data-2` stay plain `#rrggbb`**, because the
  chart code adds alpha as a hex suffix.
- **The toggle** sits in `.shell-tools` with 中/EN, as PRD `LP-0004-09` sets.
  It is a sun icon in dark and a moon in light.
- **Watch in adoption:**
  - Teal buttons and the blue 法條 flag stand out less from a teal-leaning
    ground. That is the trade the user accepted.
  - The danger tint `#2d3132` is close to neutral on the teal panel, so the
    wrong-answer box is marked mostly by its rose border and label.

## Who decided, on what evidence

Johnny Chang signed off the three theses on 2026-10-21. He picked `teal-ink`
the same day, and kept the rose danger, after reviewing the 36 shots in
`shots/`, phone first, and the three per-viewport contact sheets of them.
