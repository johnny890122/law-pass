# Design tokens

One shared contract of token names, plus one values file per design
direction. Read by [`../SKILL.md`](../SKILL.md) when it builds design-system
directions (`LP-0004-05`). The app never links this folder. Since
`LP-0004-07`, the app's tokens live in `static/css/tokens.css`, copied from
`role-hues-teal.css`. The copy here is the `LP-0004-08` record and is not kept
in sync.

**Tokens carry values, not layout.** Swapping a values file changes color,
type, spacing, radius, and shadow. It cannot turn a top nav into a bottom
tab bar. Layout differences live in each direction's artifact HTML. See "Two
Tiers" in the skill.

```text
tokens/
├── README.md
├── _structure.css    the contract: role names, placeholder values
└── <direction>.css   one per direction, named by its thesis, e.g. dense-study.css
```

`dark-neutral.css`, `dark-dim.css`, and `dark-teal-ink.css` are `LP-0004-09`'s
dark-mode variants. They are overlays, not directions: each redefines only the
tokens a dark theme changes, under `:root[data-theme="dark"]`, on top of
`static/css/tokens.css`. `dark-teal-ink.css` won and was copied into
`tokens.css`. These copies are the record and are not kept in sync.

## What earns a place in the contract

A role must pass both tests to live in `_structure.css`:

1. **Scope.** A law_pass screen renders something that needs it today. The
   bar is `templates/` (with `static/js/main.js` for toasts) and nothing
   wider. Each role's comment names the screen that needs it.
2. **Sharing.** A second direction would also have to name it, even with a
   different value. If only one direction would, it is a `--d-` token and
   lives in that direction's file only.

Fails test 1: it is not this contract's job yet. Fails test 2: it is `--d-`.

The contract is deliberately short of general. It has no image, media,
table, or monospace role, because no template renders one. **Extending the
contract is the only correct response to a missing role.** The first ticket
that renders one adds the role here and to every direction file in flight.
It never puts a literal in an artifact.

## Values files

Each `<direction>.css` defines every name in `_structure.css`, and may add
`--d-` tokens on top. Every value carries a comment naming its source:

```css
--color-accent: #1f4e79;   /* gov-portal tokens.md: .btn-primary background @1440 */
--color-accent-hover: #173b5c; /* derived: --color-accent darkened to 7:1 on --color-surface */
--d-tabbar-height: 56px;   /* gov-portal tokens.md: nav.bottom height @390 */
```

- **Captured** values cite `docs/references/<site-slug>/tokens.md`, with
  the element and viewport that file recorded.
- **Derived** values say what they were derived from and why. Contrast fixes
  and hover steps are the usual cases.
- A value with neither is not allowed. If the capture lacks a role, derive
  it in the open, or ask the user.

## Rules

- **`_structure.css` is the minimum, not the maximum.** Every values file
  defines all of it. Adding a role here means adding it to every values file.
- **Direction-only tokens are namespaced `--d-`**, such as
  `--d-sidebar-width`, and live in that direction's file only.
- **Literals live only in token files.** The system tier (base, primitives)
  and every artifact HTML go through `var(--…)`, with no hex, `rgb()`, or
  `hsl()`. The skill's hex grep enforces this.
- **Direction layout may use raw geometry**: grid tracks, widths, and
  breakpoint tweaks. Routing composition through tokens buys nothing.
- **Semantic names, not literal ones.** `--color-surface-sunken`, not
  `--color-gray-100`, so a direction can change what "sunken" looks like
  without renaming anything.
- **Contrast is part of the value.** Status and text roles must reach the
  ratio their comment in `_structure.css` states. A captured value that
  fails is replaced by a derived one, with the comment saying so.
