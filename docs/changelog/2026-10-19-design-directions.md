# 2026-10-19 — Three design-system directions; the dense-tabbar layout wins

**LP ids:** LP-0004-05

The first design-system directions derived from a reference capture are on
file in
[`artifacts/LP-0004-05-design-directions/`](../../artifacts/LP-0004-05-design-directions/).
Each of the three directions has a values file in
[`.claude/skills/neta-design/tokens/`](../../.claude/skills/neta-design/tokens/)
and renders the dashboard, the quiz question, the graded quiz, and law
detail at phone, tablet, and desktop. The user picked the `dense-tabbar`
**layout**. Its colors read gray rather than like the dotnet example, so the
palette is picked in `LP-0004-06`, and adoption moves to `LP-0004-07`. The
app does not change, so no module doc takes the decision yet.

| Area | Was | Now |
| --- | --- | --- |
| Token values | `tokens/` held only the `_structure.css` contract, with placeholder values. | `baseline.css`, `dense-tabbar.css`, and `reading-room.css` define every contract name. Each value cites a `tokens.md` row or says `derived:` and why, and every stated contrast ratio passes. |
| Type faces | The contract allowed "system stacks only". The capture's faces are the web fonts Space Grotesk and Open Sans. | System stacks stay (user, 2026-10-19). The capture's own chrome stack (`"Segoe UI", -apple-system, system-ui`) is cited, with Traditional Chinese faces added. No direction requests a font. |
| Status colors | The capture renders no success, danger, or warning color. | Derived in the open: green and amber are new, red and blue are the capture's gradient red and card blue darkened. Each reaches 4.5:1 on white and on its own tint. |
| Picked layout | Two-row header on phone, button-only dashboard, single column everywhere. | `dense-tabbar`: a top bar plus a bottom tab bar below 1024px and a left sidebar from 1024px. The dashboard opens on the five progress numbers, and law detail is two columns on desktop. A question and its options fit one phone screen. |
| System tier | — | One shared `system.css` (reset, focus ring, primitives) served all three directions with no direction-specific edit, so the system/direction split held. |

What the pick carries into adoption is in the
[`DECISION.md`](../../artifacts/LP-0004-05-design-directions/DECISION.md),
including one surprise. `/` renders the dashboard with no data today, so the
`dense-tabbar` metric strip makes adoption a route change, not only a
template change.

## Deliberately not done

- No palette was picked. `dense-tabbar.css`'s `--color-*` roles and
  `--border-width` are reopened by `LP-0004-06`.
- Nothing in `static/css/`, `templates/`, or the Python code changed. That
  is `LP-0004-07`.
- No dark mode, and no screen beyond the four in scope.
- The capture's do-not-reproduce list held: no gradient, gradient text,
  radial wash, hue rotation, logo, illustration, or copy. A Space Grotesk or
  Open Sans file was never loaded.
- `neta-design`'s Verify step does not mention the browser cache. Stale
  stylesheets from `http.server` hid a fixed overflow until the cache was
  disabled. `LP-0004-06` carries the workaround as a note. Changing the
  skill needs its own ticket.
