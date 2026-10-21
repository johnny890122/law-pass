---
id: LP-0004-09
title: Dark mode, with each learner's choice stored in user_ui_flags
type: story
status: resolved
priority: medium
created: 2026-10-20
resolved: 2026-10-21
area: ui
parent: LP-0004
tags:
  - design-system
  - dark-mode
  - artifact
  - schema
---

# Dark mode, with each learner's choice stored in user_ui_flags

## Description

Learners study at night on their phones, and the app has only a light theme.
They need a dark theme they can switch to, and it should stay switched on
every device they sign in from.

## Details

- Current:
  - `static/css/tokens.css` holds one `:root` block of light values. It is
    the only file allowed a color literal. `style.css` reads token names
    only, with no `white`, `black`, or hex. So a theme can be swapped by
    tokens alone.
  - The dotnet capture recorded light mode only
    (`docs/changelog/2026-10-18-dotnet-capture.md`, "No dark theme").
  - No per-user UI preference is stored anywhere. The language choice lives
    in `localStorage` (`appLang`), on one browser only.
  - The epic `LP-0004` listed dark mode as out of scope. This story brings
    it in.
- Desired:
  - **Two themes, light and dark. Light is the default.** The OS
    `prefers-color-scheme` setting is ignored.
  - **Dark values are derived from the light tokens.** No new capture. Every
    dark value in `tokens.css` is marked `derived:` with its reason, in the
    same comment style as the light block.
  - **Tokens.** A `:root[data-theme="dark"]` block in `tokens.css`
    redefines every token whose value changes. `style.css`, the templates,
    and JS keep reading the same names. `tokens.css` stays the only file
    with a color literal.
  - **Toggle.** A control in the shell switches the theme, with every
    `base.html` control still present at every width.
  - **Stored per user.** A new collection, `user_ui_flags`, holds one
    document per user: `{ user_id, theme, updated_at }`, unique on
    `user_id`. `theme` is `light` or `dark`. A user with no document gets
    light. This goes through `schema-check`.
  - **No flash.** Signed-in pages render in the stored theme from the
    server, so a dark user never sees a light frame first.
  - **Signed-out pages stay light.** The login page has no user, so it
    renders the default theme. The Google and LINE buttons keep their
    `--brand-*` light values.
  - **Charts.** `/progress` reads `--color-data-1` and `--color-data-2`
    through `getComputedStyle`. They show the active theme's values.
- Scope: `static/css/tokens.css`, `templates/base.html`,
  `static/js/main.js`, `static/css/style.css` (the toggle's row),
  `db/models.py`
  (`init_db()` and a dataclass), one new route to save the choice, and
  `tests/`.
- Artifact required. The visual question: **what does the derived dark
  palette look like?** Three variants in `artifacts/LP-0004-09-dark-mode/`,
  built with `neta-design`. They differ only in how dark the ground is and
  how panels separate from it:
  - **`neutral`**: neutral near-black ground. Panels are one lightness step
    above it, the way light mode's white panels sit on `#f5f5f5`.
  - **`dim`**: a softer, lighter dark gray ground and off-white text, for
    long law reading with less glare.
  - **`teal-ink`**: the ground and panels carry a faint teal hue, so the
    main color sets the mood.
- Not open, so every variant respects these:
  - Everything in `LP-0004-08`'s `DECISION.md` and
    `docs/modules/ui/index.md` except color values. That covers the
    `dense-tabbar` layout, the ledger, panel, and sheet containers, the
    index tabs, 黑體 only, type, spacing, radius, and the breakpoints.
  - **The role map keeps its meanings.** Teal is the main color, blue is
    法條, magenta is 簡答題, and flamingo is the streak. A hue may change
    lightness for dark, never meaning.
  - **Contrast holds as in light:** text at 4.5:1 on its ground, a label on
    the accent fill at 4.5:1, and flags at 3:1 as graphics.
  - Status colors stay semantic. No gradient, gradient text, or glow.
  - The toggle sits in the same place in every variant, so the palette is
    the only thing compared.
- PRD: `docs/prd/LP-0004-09-dark-mode.md`. A new route, a new collection,
  and the shell together need exact contracts.
- Out of scope:
  - A "follow the system" option, and reading `prefers-color-scheme`.
  - Moving `appLang` or any other preference into `user_ui_flags`.
  - Dark mode on the login page, and dark `--brand-*` values.
  - Any layout, type, spacing, or copy change beyond the toggle's own
    label.

## Acceptance Criteria

- [x] The three variant theses, one sentence each, are signed off by the
      user before any HTML is written.
- [x] Variants in `artifacts/LP-0004-09-dark-mode/` screenshot at phone
      (390x844), tablet (768x1024), and desktop (1440x900), reviewed with
      the user; choice recorded in `DECISION.md`.
- [x] `tokens.css` holds a `:root[data-theme="dark"]` block with the
      winner's values, each marked `derived:` with its reason. The
      `neta-design` hex grep prints nothing outside `tokens.css`.
- [x] Contrast holds in dark: text at 4.5:1 on bg, surface, and sunken; a
      label on the accent fill at 4.5:1; every flag at 3:1 on bg and
      surface. The ratios are written in the value comments.
- [x] `user_ui_flags` exists through `schema-check`: documented in
      `docs/modules/db/data-model.md`, its unique `user_id` index built by
      `init_db()`, and `tests/test_schema_drift.py` green.
- [x] Switching the theme writes the learner's `user_ui_flags` document.
      Signing in on another browser renders the stored theme with no light
      flash.
- [x] A user with no document, and the login page, render light.
- [x] The save route accepts only `light` and `dark`, and refuses a
      signed-out request.
- [x] `/progress` charts read the dark data colors in dark mode.
- [x] `pytest` green — covered by `tests/test_app.py` (or a new
      `tests/test_ui_flags.py`, as the PRD sets): save each value, reject
      a bad value, reject signed-out, and render `data-theme` from the
      stored flag and from no document.
- [x] `flake8` clean.
- [x] Seen working in the running app: `python app.py`, switch to dark,
      reload, and sign in again. (Sign-in again was a second browser context
      with a freshly minted session: real OAuth cannot finish locally.) Every
      page passes the
      `docs/modules/ui/index.md` check at phone 390x844, tablet 768x1024,
      and desktop 1440x900, in both themes, and the screenshots are looked
      at.
- [x] Docs synced: `docs/modules/ui/index.md` (themes, the toggle, and
      where dark tokens live), `docs/modules/db/data-model.md` (through
      `schema-check`), and a changelog entry.
- [x] PRD tickets only: report at
      `docs/reports/LP-0004-09-dark-mode/report.md` is approved.

## Open Questions

- None.

## Related Files

- `static/css/tokens.css`
- `static/css/style.css` (the `.shell-tools` row for the toggle, per the PRD)
- `templates/base.html`
- `templates/progress.html` (no change: a switch reloads, per the PRD)
- `templates/login.html` (stays light)
- `static/js/main.js`
- `db/models.py`
- `services/auth.py`
- `routes/` (the save route; the PRD sets the file)
- `app.py`
- `tests/test_app.py`
- `tests/test_schema_drift.py`
- `tests/test_design_tokens.py`
- `docs/modules/ui/index.md`
- `docs/modules/db/data-model.md`
- `.claude/skills/neta-design/tokens/_structure.css`
- `artifacts/LP-0004-08-main-color/` (the body markup to copy)
- `artifacts/LP-0004-09-dark-mode/`

## Handoff Appendix

### Settled Decisions

Confirmed with the user on 2026-10-20:

- Two themes, light and dark, with light as the default. No system option.
- Dark values are derived from the light tokens, not captured.
- The collection is named `user_ui_flags`, matching the other per-user
  collections. The user asked for a "uiflag" collection, and the name
  follows the `user_*` convention.

Following from those answers, for the user to confirm at PRD review:

- The login page renders light, since no user and no OS reading means the
  default applies.
- The collection holds one field per flag, and `theme` is the only flag
  today. A future flag adds a field through `schema-check`.

### Behavior Details

For the PRD to fix exactly:

- **Rendering.** `base.html` puts `data-theme` on `<html>` from the stored
  flag, so the first paint is right. Reading it needs either one indexed
  `find_one` per page render, or a copy kept in the Flask session, set at
  sign-in and on every save. The session copy avoids a read per page. The
  collection stays the source of truth.
- **Toggle.** A likely home is `.header-right`, beside 中/EN, as an icon
  button at every width. The phone top bar is already full (logo, select,
  中/EN, logout), so the artifact must show it fits at 390px. The PRD sets
  its copy.
- **Switching.** The toggle saves the choice, then either sets
  `data-theme` in place or reloads, as the language toggle does. Setting it
  in place leaves the progress charts on stale colors unless they redraw.
  The PRD picks one.
- **Save route.** It takes `{ "theme": "light" | "dark" }`, upserts on
  `user_id`, and sets `updated_at`. `login_required` redirects rather than
  returning 401, so the PRD says what a signed-out JSON call gets.

### Data And LLM Notes

- `user_ui_flags`: `user_id` ObjectId (written like every other
  `user_id`), `theme` str, `updated_at` datetime UTC. Unique index
  `user_id_1`. No migration: an absent document means light.
- `schema-check` should also decide whether
  `scripts/migrations/20261016_remove_username_only_users.py` lists the new
  collection with the other per-user collections.
- No LLM involvement.

### Test Scenarios

- `PUT` (or `POST`) the save route with `dark`, then `light`: one document
  per user, `theme` updated, `updated_at` set.
- A bad value (`blue`, missing, not a string): 400 and nothing written.
- Signed out: refused and nothing written.
- `GET /` for a user with `theme: dark` renders `data-theme="dark"`. With no
  document it renders light. `GET /auth/login` renders light.
- `tests/test_design_tokens.py` stays green with the dark block in
  `tokens.css`.

### Deferred Decisions

- A "follow the system" option: not planned. A new ticket if wanted.
- Moving `appLang` from `localStorage` into `user_ui_flags`: not planned.

## Resolution

Learners can switch to the derived `teal-ink` dark theme with a toggle beside
中/EN. The choice is stored per learner in the new `user_ui_flags` collection
and rendered on `<html>` by the server, so there is no light flash, and login
stays light. It is live as Heroku v14, with production's `user_id_1` index
confirmed. A "follow the system" option, moving `appLang` into the flags, and
a dark login page were left out. See [the changelog entry](../../../changelog/2026-10-21-dark-mode.md)
and [the approved report](../../../reports/LP-0004-09-dark-mode/report.md).
