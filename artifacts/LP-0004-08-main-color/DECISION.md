# LP-0004-08 · Decision

**Question:** which main color should `role-hues` carry: purple, blue, or
teal?

## Winner: `teal`

Values file: `.claude/skills/neta-design/tokens/role-hues-teal.css`, with
this folder's `system.css`, `dense-tabbar-layout.css`, and
`role-hues-color.css`.

Teal `#00727a` is the main color: actions, links, the active tab, the
progress fill, 選擇題, and 作答題數. 法條 stays blue, 簡答題 magenta, and the
streak flamingo. It is the one value from outside the dotnet capture, at hue
184°, 37° from success green and 32° from info blue.

## Rejected

- **`purple`** (`role-hues.css`): the `LP-0004-06` baseline, kept for
  comparison. The user preferred teal.
- **`blue`** (`role-hues-blue.css`): the captured blue had to be darkened
  to `#0061f5` to pass as text. It then sits 1.16:1 from info blue, so the
  AI 解析 callout reads like an info notice. 法條 had to move to purple.

## What the real implementation must keep

- Everything in `LP-0004-06`'s `DECISION.md` (the `role-hues` frame), with
  teal in place of purple.
- **The accent family**, all derived from teal by the capture's own purple
  steps:

  | Role | Value | How it is derived | Contrast |
  | --- | --- | --- | --- |
  | Main | `#00727a` | — | 5.69:1 surface, 5.22:1 bg, 4.94:1 on its tint; white label 5.69:1 |
  | Hover | `#005b62` | Main × 0.8 lightness | — |
  | Surface | `#e6f1f2` | Main at 0.098 alpha over white | — |

  `--color-link` and `--color-data-1` follow the main color.
- **Flag tokens are named by meaning**: `--d-flag-law`, `--d-flag-short`,
  and `--d-flag-streak`. The main color's flags read `--color-accent`.
- **Watch in adoption:** the teal tint `#e6f1f2` is close to the success
  tint `#e7f4ec`. On the graded quiz, the AI 解析 callout sits right under
  the green correct answer, and the two pale boxes look alike. Adoption
  should keep them apart: a different callout treatment, or a rule between
  them.

## Who decided, on what evidence

Johnny Chang picked `teal` on 2026-10-19, after reviewing the 36 shots in
`shots/`, phone first, with `purple` as the baseline. In the same message he
asked for the decisions so far to be applied to the real app, which is
`LP-0004-07`.
