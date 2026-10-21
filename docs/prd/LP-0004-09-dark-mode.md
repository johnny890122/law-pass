---
ticket: LP-0004-09
status: approved
created: 2026-10-20
approved: 2026-10-20
reviewer: Johnny Chang
---

# PRD: Dark mode, with each learner's choice stored in user_ui_flags

Implements `LP-0004-09`, filed as `LP-0004-09-dark-mode.md` and listed in
[docs/issues/](../issues/README.md). Its folder follows its status. Behavior,
scope, and settled decisions live in the ticket and are not restated here.

The dark values come from the ticket's artifact, which is built after this
PRD is approved and before any code (Implementation Order step 1). This PRD
fixes every contract around those values. It does not pick them:
`artifacts/LP-0004-09-dark-mode/DECISION.md` will.

Settled at gap analysis (user, 2026-10-20):

- The theme is read per page render with one indexed `find_one`, not kept
  in the Flask session.
- A toggle click saves, then reloads the page.
- The save route is `PUT /api/ui-flags/theme`, and a signed-out call gets
  401 JSON.
- The toggle is an icon button labeled 「深色模式」 with `aria-pressed`.

## Before → After

### Theme tokens

- **Before** (`docs/modules/ui/index.md` § Tokens and type,
  [tokens.css:22-136](../../static/css/tokens.css#L22-L136)):
  1. `tokens.css` holds one `:root` block of light values. It is the only
     file with a color literal, and `tests/test_design_tokens.py` enforces
     that.
  2. Nothing sets `color-scheme`, so native controls draw light.
- **After:**
  1. `:root` gains `color-scheme: light`. A new
     `:root[data-theme="dark"]` block follows the `:root` block. It sets
     `color-scheme: dark` and redefines every token whose value changes,
     using the `DECISION.md` winner's values.
  2. Each dark value carries a `derived:` comment with its reason and its
     contrast ratios, in the light block's style.
  3. The dark block never redefines `--brand-*`, type, space, radius,
     layout, or motion tokens.
  4. `--color-data-1` and `--color-data-2` stay plain `#rrggbb` in dark,
     because the chart code adds alpha as a hex suffix
     ([progress.html:66](../../templates/progress.html#L66)).
  5. `--color-focus` is redefined, because the light value `#000000` is
     invisible on a dark ground.

### Rendering a signed-in page

- **Before** ([base.html:2](../../templates/base.html#L2)): every page but
  login extends `base.html`, which opens `<html lang="zh-TW">`. No
  per-user UI state is read anywhere. The only other preference, `appLang`,
  lives in `localStorage`
  ([main.js:58-68](../../static/js/main.js#L58-L68)).
- **After:**
  1. `routes/frontend.py` registers an app-wide context processor
     (`@frontend_bp.app_context_processor`) that supplies `theme` to every
     `render_template`.
  2. With `user_id` in the session, it runs
     `user_ui_flags_collection.find_one({"user_id": ObjectId(user_id)}, {"theme": 1})`.
     `theme` is `"dark"` when that document's `theme` is `"dark"`, and
     `"light"` otherwise, including when there is no document. With no
     `user_id`, it is `"light"` and nothing is read.
  3. `base.html` opens `<html lang="zh-TW" data-theme="{{ theme }}">`. The
     attribute is in the HTML before the first stylesheet loads, and no
     script sets the theme on load. So a dark learner's first frame is
     dark.
  4. `login.html` does not extend `base.html` and is not changed. It has no
     `data-theme`, so it renders the `:root` light values.

### Toggle in the shell

- **Before** ([base.html:37-52](../../templates/base.html#L37-L52),
  `docs/modules/ui/index.md` § The shell): `.header-right` holds
  `.lang-toggle` (中/EN) and `.user-menu` (user name, logout). It is a row
  below 1024px ([style.css:389](../../static/css/style.css#L389)) and a
  stretched column at the bottom of the sidebar from 1024px
  ([style.css:1016-1018](../../static/css/style.css#L1016-L1018)).
- **After:**
  1. Inside `.header-right`, a new `<div class="shell-tools">` wraps
     `.lang-toggle` and the new toggle, ahead of `.user-menu`. Below 1024px
     the top bar reads: logo, select, 中/EN, toggle, logout. From 1024px
     the toggle shares 中/EN's row in the sidebar.
  2. The toggle is
     `<button id="theme-toggle" class="icon-btn" title="深色模式" aria-label="深色模式" aria-pressed="true|false">`.
     `aria-pressed` is `true` in dark.
  3. The server picks the icon: a moon in light, a sun in dark. Both are
     inline SVGs with `stroke="currentColor"`, like the logout icon.
  4. It shows for every law type. `main.js` hides only `.lang-toggle`
     ([main.js:202-206](../../static/js/main.js#L202-L206)), so the
     wrapper keeps the toggle in place when 中/EN is hidden.
  5. `style.css` gains one base rule,
     `.shell-tools { display: flex; align-items: center; gap: var(--space-3); }`.
     It drops the sidebar's `.lang-toggle { align-self: flex-start; }`
     ([style.css:1017](../../static/css/style.css#L1017)), which the
     wrapper row makes redundant.
  6. At 390px on patent-act, where 中/EN shows, the select keeps about
     130px. That fits 「專利法 (168)」. The other law types hide 中/EN, which
     gives the select about 94px more.

The ticket's Related Files says `style.css` "should need no change". Step 5
contradicts that note, and the ticket gets refined to match.

### Switching

- **Before:** none (new). The language toggle is the precedent: save the
  choice, then `window.location.reload()`
  ([main.js:63-68](../../static/js/main.js#L63-L68)).
- **After:**
  1. A click on `#theme-toggle` computes the next theme from
     `document.documentElement.dataset.theme`: `dark` becomes `light`, and
     anything else becomes `dark`.
  2. It calls the existing `apiCall('/api/ui-flags/theme', { method: 'PUT', body: JSON.stringify({ theme: next }) })`
     ([main.js:265-286](../../static/js/main.js#L265-L286)).
  3. On success it calls `window.location.reload()`. The server renders the
     new `data-theme` and icon, and `/progress` rebuilds its charts from the
     new token values.
  4. On failure `apiCall` already shows its error toast, and the page stays
     as it was.

### Progress charts

- **Before** ([progress.html:64-71](../../templates/progress.html#L64-L71)):
  the chart script reads `--color-data-1`, `--color-data-2`,
  `--color-text-muted`, `--color-border`, and `--font-body` from
  `getComputedStyle(document.documentElement)` once, when the page loads.
- **After:** unchanged. Every theme switch reloads the page, so the script
  always reads the active theme's values. The ticket lists `progress.html`
  in scope for the in-place option, which was not picked.

## Route Contracts

### `PUT /api/ui-flags/theme`

- **Auth:** no `login_required`, because it redirects with 302 and `fetch`
  would follow that silently. The route reads `get_current_user()` itself.
- **Request:** JSON body `{"theme": "light" | "dark"}`, read with
  `request.get_json(silent=True)`.
- **Response:** `200 {"theme": "<value>"}`, after
  `update_one({"user_id": ObjectId(user_id)}, {"$set": {"theme": value, "updated_at": datetime.utcnow()}}, upsert=True)`.
- **Errors:**
  - Signed out: `401 {"error": "Not authenticated"}`, as `/auth/current`
    returns ([routes/auth.py:126-127](../../routes/auth.py#L126-L127)).
    Nothing is written.
  - Any of the following gets `400 {"error": "theme 必須是 light 或 dark"}`
    (proposed), and nothing is written:
    - a body that is not JSON, or not a JSON object;
    - a missing `theme`;
    - a `theme` that is not exactly the string `light` or `dark`.
  - A database failure: Flask's 500. `apiCall` toasts it.

### Every page that extends `base.html`

- **Auth:** `login_required`, unchanged.
- **Response:** unchanged, except that `<html>` carries
  `data-theme="light"` or `data-theme="dark"`, set as in Rendering, step 2.

### `GET /auth/login`

- Unchanged. No `data-theme`, so it renders light.

## Data Changes

Each change goes through `schema-check` at implementation. Nothing here is
final until that skill writes `docs/modules/db/data-model.md`.

| Collection | Change | Existing documents | Migration |
| --- | --- | --- | --- |
| `user_ui_flags` | New collection, one document per user. Fields: `user_id` ObjectId (`users._id`), `theme` str (`light` or `dark`), and `updated_at` datetime UTC. Unique index `user_id_1` on `[("user_id", 1)]`, built in `init_db()`. Dataclass `UserUiFlagsModel` in `db/models.py`, with `user_ui_flags_collection` exported beside the other per-user collections. The only writer is `PUT /api/ui-flags/theme` (an upsert). | None exist. A missing document means light. | none |
| `scripts/migrations/20261016_remove_username_only_users.py` | `PER_USER` gains `user_ui_flags`, so the LP-0002-01 cleanup also removes the flags of the users it deletes. `schema-check` confirms the change. `tests/test_migrations.py` iterates `PER_USER`, so it covers the new entry with no change. | — | edited, no new script |

A same-moment first save from two browsers cannot create two documents. The
unique index refuses the second insert, and MongoDB 4.2+ retries an upsert
that hits a duplicate key on its equality field. The app has no retry code.

## Templates and UI Copy

- `templates/base.html`:
  - `data-theme="{{ theme }}"` on `<html>`;
  - the `.shell-tools` wrapper;
  - the toggle button, whose icon follows `theme`.
- `static/css/tokens.css`: `color-scheme` and the dark block.
- `static/css/style.css`: the `.shell-tools` rule in, and the sidebar
  `.lang-toggle` alignment rule out.
- `static/js/main.js`: the toggle's click handler, beside the language
  toggle's.
- `templates/login.html` and `templates/progress.html`: no change.
- Copy:
  - Toggle `title` and `aria-label`: 「深色模式」 (proposed). It stays the
    same in both themes, and `aria-pressed` carries the state.
  - 400 error: 「theme 必須是 light 或 dark」 (proposed). It is an API
    message, shown only through `apiCall`'s toast if a client sends a bad
    value.
  - Failure toast: the existing `apiCall` copy
    ([main.js:275-283](../../static/js/main.js#L275-L283)), with no new
    string. It shows the server's `error` when the reply is JSON with one. A
    reply that is not JSON, such as Flask's 500 page, shows `HTTP` and the
    status code, for example 「HTTP 500」. A network failure shows the
    browser's own message, and an empty message falls back to
    「請求失敗，請稍後再試」. (Refined at the report on 2026-10-21, with the
    user. The draft named only the first and last cases. The code was
    unchanged.)

## LLM Prompts

None — the feature makes no LLM call.

## Business Rules and Edge Cases

| ID | Rule or scenario | Expected behavior |
| --- | --- | --- |
| BR-1 | No document, or a `theme` other than `dark` | The page renders `data-theme="light"`. |
| BR-2 | Stored `dark` | Every `base.html` page renders `data-theme="dark"` in its HTML. No script sets the theme on load, so no light frame shows first. |
| BR-3 | Another browser | After a switch on browser A, browser B renders the new theme on its next page load, whether it was already signed in or signs in fresh. |
| BR-4 | Login and signed-out pages | `/auth/login` renders light, including after a dark learner logs out. The `--brand-*` values are unchanged. |
| BR-5 | OS setting | Ignored. `prefers-color-scheme` appears nowhere in `static/` or `templates/`. |
| BR-6 | Dark tokens | They redefine only tokens whose value changes. Each is marked `derived:` with its reason. The comments record these ratios: text 4.5:1 on bg, surface, and sunken; the accent label 4.5:1 on the accent fill; each flag 3:1 on bg and surface; `--color-focus` 3:1 on bg and surface. Only `tokens.css` holds a color literal. |
| BR-7 | Role map | Teal, blue (法條), magenta (簡答題), and flamingo (streak) keep their meanings in dark. Status colors mark status only. No gradient, gradient text, or glow. |
| BR-8 | Toggle presence | It shows on every `base.html` page, at every width, for every law type, with a 44px target. Every other shell control stays. |
| BR-9 | Charts | In dark, `/progress` draws with the dark `--color-data-1` and `--color-data-2`, and its axes and grid use the dark `--color-text-muted` and `--color-border`. |
| BR-10 | Native controls | In dark, `color-scheme: dark` makes the law-type select's popup and the scrollbars draw dark. |
| BR-11 | Save validation | Only the exact strings `light` and `dark` are accepted. `"Dark"`, `"blue"`, `1`, `null`, a missing key, a JSON array, or a non-JSON body gets 400 and writes nothing. |
| BR-12 | Signed-out save | 401 JSON, and nothing is written. |
| BR-13 | Failed save | `apiCall` shows its toast. There is no reload, and the theme stays as it was. |
| BR-14 | Three viewports, two themes | Every page passes the `docs/modules/ui/index.md` check at 390x844, 768x1024, and 1440x900, in light and in dark. |

## Test Plan

No external calls. Sessions are set with `client.session_transaction()`
through the existing `signed_in` fixture. Its teardown also deletes the
user's `user_ui_flags` document.

- `tests/test_app.py`, new class `TestUiFlags`:
  - **Save dark, then light.** Signed in as U: `PUT /api/ui-flags/theme`
    with `{"theme": "dark"}` → 200 `{"theme": "dark"}`. Exactly one
    `user_ui_flags` document for U, with `theme` `dark` and a datetime
    `updated_at`. `PUT` again with `{"theme": "light"}` → 200. Still one
    document, with `theme` `light` and an `updated_at` no earlier than
    before.
  - **Bad values** (parametrized): `{"theme": "blue"}`,
    `{"theme": "Dark"}`, `{}`, `{"theme": 1}`, `{"theme": null}`,
    `["dark"]`, and a `text/plain` body `dark` → each 400, with zero
    documents for U.
  - **Signed out:** a fresh client, `PUT` with `{"theme": "dark"}` → 401
    `{"error": "Not authenticated"}`. The collection count is unchanged.
  - **Render from the flag:** U with a `theme: dark` document → `GET /`
    and `GET /progress` each contain `data-theme="dark"` and
    `aria-pressed="true"`.
  - **Render with no document:** a fresh U → `GET /` contains
    `data-theme="light"` and `aria-pressed="false"`.
  - **Login stays light:** `GET /auth/login` → 200, with no `data-theme`
    in the body.
- `tests/test_design_tokens.py`:
  - **Dark names exist in light:** every `--name` declared in the
    `:root[data-theme="dark"]` block is also declared in `:root`. A
    misspelled dark name would do nothing silently.
  - **No OS reading:** `prefers-color-scheme` appears in no file under
    `templates/`, `static/js/`, or `static/css/`.
  - The existing contract and literal tests stay green, with the dark
    block inside `tokens.css`.
- `tests/test_schema_drift.py`: unchanged. It goes green once
  `data-model.md` documents `user_ui_flags`, its `user_id_1` index, and
  `UserUiFlagsModel`.
- `tests/test_migrations.py`: unchanged. It covers the new `PER_USER`
  entry.

The contrast ratios, the three-viewport check in both themes, the
second-browser sign-in, and the chart colors are the Seen working step,
done in Playwright against `python app.py`, not in `pytest`.

## Rollout and Migration

- No new env vars or config.
- On Heroku, `init_db()` builds `user_ui_flags.user_id_1` at boot. The
  collection is new and empty, so the unique build cannot fail. Two
  gunicorn workers calling `create_index` on the same spec is a no-op for
  the second worker, unlike the `drop_index` race in the LP-0009 release.
- After deploy, a production check confirms `user_id_1` exists. That check
  fills the `Ran` cell of the `data-model.md` Change Log row, and the
  ticket cannot resolve without it.
- Rollback: revert the commit. Any `user_ui_flags` documents left behind
  are inert without the code and can stay.

## Implementation Order

1. **Artifact** (`neta-design`, no code):
   - The user signs off the three variant theses.
   - Build `neutral`, `dim`, and `teal-ink` in
     `artifacts/LP-0004-09-dark-mode/`, with the toggle in the
     `.shell-tools` position from Toggle in the shell.
   - Shoot each at the three viewports.
   - The user picks, and the pick goes into `DECISION.md`.
   - `pytest` is untouched.
2. **Schema:**
   - Run `schema-check` for `user_ui_flags` and the `PER_USER` entry.
   - Add `UserUiFlagsModel`, the collection, its export, and the
     `init_db()` index in `db/models.py`.
   - Edit `PER_USER`.
   - The drift and migration tests are green.
3. **Save route:** `PUT /api/ui-flags/theme` in `routes/frontend.py`, with
   the save, bad-value, and signed-out tests.
4. **Render and toggle:**
   - The context processor, `data-theme` and the toggle in `base.html`,
     the `.shell-tools` rule in `style.css`, and the handler in `main.js`.
   - The render and login tests.
   - Refine the ticket's `style.css` and `progress.html` notes.
5. **Dark tokens:**
   - `color-scheme` and the `:root[data-theme="dark"]` block in
     `tokens.css`, from `DECISION.md`, with ratios in the comments.
   - The two new `test_design_tokens.py` tests.
6. **Seen working:**
   - `python app.py`: switch to dark, reload, sign in on a second browser
     context, and check `/progress`.
   - Every page at the three viewports in both themes, with the
     screenshots looked at.
7. **Docs:**
   - `docs/modules/ui/index.md`: themes, the toggle, and where the dark
     tokens live.
   - A changelog entry and its `changelog/index.md` row.
   - Then `prd-report`.
