---
ticket: LP-0004-07
status: approved
created: 2026-10-19
approved: 2026-10-20
reviewer: Johnny Chang
---

# PRD: Adopt the dense-tabbar layout and teal role-hues palette on every page

Implements `LP-0004-07`, filed as `LP-0004-07-adopt-design-system.md` and
listed in [docs/issues/](../issues/README.md). Its folder follows its status.
Behavior, scope, and settled decisions live in the ticket and are not
restated here.

The look being adopted is specified by three decision records. This PRD maps
them onto the real templates and does not repeat them:

- [`LP-0004-05` DECISION](../../artifacts/LP-0004-05-design-directions/DECISION.md):
  the `dense-tabbar` layout.
- [`LP-0004-06` DECISION](../../artifacts/LP-0004-06-color-variants/DECISION.md):
  the `role-hues` frame (ledger, panel, sheet, index tabs, flags).
- [`LP-0004-08` DECISION](../../artifacts/LP-0004-08-main-color/DECISION.md):
  teal.

The reference implementation is the CSS in
`artifacts/LP-0004-08-main-color/`: `system.css`, `dense-tabbar-layout.css`,
and `role-hues-color.css`, plus
`.claude/skills/neta-design/tokens/role-hues-teal.css`.

## Before → After

### Stylesheets and tokens

- **Before** ([templates/base.html:10-16](../../templates/base.html#L10-L16)):
  1. `base.html` links the MUI 0.10.3 CSS, the Figma
     `static/css/design-tokens.css`, and then `static/css/style.css`.
  2. `style.css:4-21` aliases 15 legacy names (`--primary-color`,
     `--border-color`, and the rest) onto Figma tokens. Its rules read 31
     token names, and 28 color literals sit directly in its rules.
  3. `login.html` links MUI on its own and carries 28 literals. The
     templates carry 75 inline `style=` attributes, and `main.js:242`
     colors toasts with literals.
- **After:**
  1. `base.html` and `login.html` link `static/css/tokens.css`, then
     `static/css/style.css`. No MUI asset loads.
  2. **`tokens.css`** is the app's one token file and the only file that
     holds a color literal:
     - It copies `role-hues-teal.css`, with every source comment.
     - It adds a `--brand-*` section for third-party marks (BR-8).
     - From here on it is the source of truth. The skill's copy stays as
       the `LP-0004-08` record and is not kept in sync.
  3. **`style.css`** is rewritten in this order: base and primitives (from
     the artifact `system.css`), the shell and containers (from
     `dense-tabbar-layout.css`), the flags (from `role-hues-color.css`),
     and then one section per page. It reads contract names only. The
     legacy alias layer and `design-tokens*.css` are deleted.
  4. Inline `style=` attributes that set a color, spacing, or type value
     move into `style.css` classes. A `style=` that only toggles state, such
     as `display: none` or a progress `width`, may stay.

### Shell (every page but login)

- **Before** (`docs/modules/ui/index.md` § Header by range; `base.html:21-56`):
  a sticky header in two rows on phone and one row from 768px.
- **After:** the `dense-tabbar` shell, per the `LP-0004-05` DECISION:
  1. `<header class="shell">`, with no inner wrapper, holds these in order:
     - `a.logo`;
     - `div.law-type-selector.select-wrap > select#law-type-select`;
     - `nav.nav`, whose four `a.nav-link` each wrap their label in a
       `<span>`;
     - `div.header-right`, holding `.lang-toggle` and `.user-menu`, which
       holds `span#user-display-name.user-name` and
       `button#logout-btn.icon-btn.btn-logout`.

     Every `id` stays, so `main.js` keeps working unchanged.
  2. Active link: as today, from `request.path`. `/` gives 首頁,
     `/laws*` 法條瀏覽, `/question-bank` 題庫, and `/progress` 我的進度.
     Other paths mark none.
  3. Below 1024px there is a sticky top bar and a fixed bottom tab bar.
     The active tab is marked on its top edge, and the user name is
     hidden. From 1024px there is a fixed left sidebar.
  4. The body pads the tab bar plus `env(safe-area-inset-bottom)`. The
     viewport meta gains `viewport-fit=cover`.

### Dashboard `/`

- **Before** ([routes/frontend.py:12-20](../../routes/frontend.py#L12-L20);
  `templates/dashboard.html`): renders `dashboard.html` with no context. The
  page is one card of three buttons, plus a tips card under 「💡 學習小提示」
  with inline styles.
- **After:**
  1. `dashboard()` calls `get_progress_summary(get_current_user(), None,
     get_current_law_type())` and renders `dashboard.html` with
     `summary=…`.
  2. The page renders, in order:
     - the ledger: five rows of label and number, as in the
       `LP-0004-06` DECISION;
     - the start block: 開始新測驗 at full width, then 法條瀏覽 and
       我的題目 side by side;
     - the tips, as a ruled list under 「學習小提示」.

     From 1024px the ledger spans the top, with the start block and the
     tips side by side under it.

### Law detail `/laws/<law_id>`

- **Before:** `templates/law_detail.html`:
  - The law and its related questions are `.card` blocks with 31 inline
    styles.
  - The meta line is `.stat-badge` with 📊 and ✓ icons.
  - The filter tabs are pills.
- **After:**
  - **Sheet.** The law is a sheet with `--radius-sm` corners and the 法條
    flag on its top edge. The meta line keeps ✓ and drops the 📊 span.
  - **Related questions panel.** The related questions sit in a panel
    with index tabs, a ruled list, the 選擇題 (teal) and 簡答題 (magenta)
    flag badges, and the flag keys on those two tabs.
  - **Desktop.** From 1024px there are two columns, with the sheet sticky.
  - **Error state.** 「⚠️ 載入失敗」 stays and is colored by
    `--color-danger`. Today it reads `var(--error-color)`, which no layer
    defines.

### Quiz config `/quiz/config` and session `/quiz/session/<id>`

- **Before:** `quiz_config.html`:
  - Radio cards for type (選擇題 / 簡答題 / 混合題型) and mode
    (新題 / 複習 / 混合), plus `.count-btn` buttons.
  - A 「💡 說明」 card, with six inline styles.

  `quiz_session.html`:
  - The question card, the result card with a filled callout, the summary
    card, and the report modal.
- **After:**
  - **Config.** The form is one panel:
    - The radio cards take the `mcq-option` treatment: the selected one
      gets an accent outline and accent surface.
    - The 選擇題 and 簡答題 cards carry their flag keys.
    - The count buttons become a segmented control styled like
      `.lang-toggle`.
    - 「說明」 is a ruled list under the panel.
  - **Question.** It matches the mock: the progress row, then a panel with
    the badge and 第 N 題 on one line, the stem, and the options.
  - **Graded.** The result panel matches the mock, except that
    「AI 解析（重點）」 has **no fill**: a rule above it, and its label in
    `--color-accent` (BR-10).
  - **Summary.** 「🎉 測驗完成！」 stays, because it is a title rather than
    a section marker. The four `summary-stat` blocks become a ledger
    inside the panel.
  - **Report modal.** 「📢 回報題目問題」 stays and is restyled on tokens.

### Laws list `/laws`

- **Before:** `laws.html` has a filter section (search bar, then a
  collapsible chapter selector of `.chapter-tab` pills) and `.law-item`
  cards built in JS.
- **After:**
  - The search bar is a field.
  - The chapter selector's tabs become index tabs.
  - `.law-list` is one ruled list. Each row holds 第 N 條, the
    `.chapter-badge` as a neutral count badge, the excerpt, and the star,
    with no card per item.

### My questions `/my-questions` and question bank `/question-bank`

- **Before:** `.tab-btn` and `.filter-btn` button rows, with one `.card`
  per question built in JS. Each page carries about 10 literals.
- **After:**
  - The tab and filter rows become index tabs.
  - The questions sit in one panel as a ruled list, like law detail's
    related questions.
  - Type badges are flags. MCQ is `badge-mcq`, in teal. SA is
    `badge-short`, in magenta, even though these pages label it
    「問答題」 (copy unchanged).
  - `score-badge` keeps its status colors.
  - The `.pager` card stays a panel.

### Progress `/progress`

- **Before:** `progress.html` has `.range-btn` pills, five `.metric-card`
  tiles, two chart blocks with literal Chart.js colors
  ([progress.html:107-124](../../templates/progress.html#L107-L124)), and a
  `.legacy-notice`.
- **After:**
  - The range buttons are index tabs, and the metric cards are the
    dashboard's ledger.
  - Each chart is a panel. Chart.js reads `--color-data-1` (teal bars) and
    `--color-data-2` (neutral line) through `getComputedStyle`, at alpha
    0.6 for the bar fill and 0.1 for the line fill.
  - `.legacy-notice` is an info-status block on `--color-info-surface`.

### Login `/auth/login`

- **Before:** `login.html` stands alone. It has the MUI CSS, a purple
  gradient background (`:11`, `:163`), literal Google and LINE button
  colors, the Google "G" as inline SVG with four literal fills, and
  literal alert colors.
- **After:**
  - The page is a single panel centered on `--color-bg`, with no
    gradient. It links `tokens.css` and `style.css`, and no shell.
  - The Google button follows Google's sign-in branding (white fill and a
    `--brand-google-border` outline), with the logo as
    `<img src="/static/img/google-g.svg">`.
  - The LINE button uses `--brand-line` with white text.
  - Alerts use the danger and success status pairs.

### Toasts

- **Before** ([static/js/main.js:233-256](../../static/js/main.js#L233-L256)):
  `showToast` sets literal background colors through `style.cssText`.
- **After:** `showToast` sets only `className = 'toast toast-<type>'`, and
  `style.css` colors the toasts:
  - `.toast-success`, `.toast-error`, and `.toast-info` from the success,
    danger, and info pairs;
  - `.toast-warning` from warning;
  - shadow and placement from the tokens.

## Route Contracts

### `GET /`

- **Auth:** `@login_required`, unchanged. Without `user_id` in the session,
  it returns a 302 to `auth.login` with `next`.
- **Request:** no fields. It reads `session['user_id']` and
  `session['current_law_type']`, which defaults to `patent-act`.
- **Response:** 200, rendering `dashboard.html` with `summary`, the dict from
  `get_progress_summary(user_id, None, law_type)`. The template reads:
  - `summary.streak`, `summary.questions_answered`,
    `summary.mastered_count`, and `summary.laws_covered` (integers);
  - `summary.avg_score_rate` (a float, rendered `"%.1f"|format(...)` then
    `%`).
- **Errors:** a database error propagates as a 500, as in `/progress`
  today. No new handling.

No other route changes. `/progress` and every API keep their contracts.

## Data Changes

None — `/` reads `user_daily_stats` and the legacy collections through the
existing `get_progress_summary`. No field, index, or collection changes, so
`schema-check` does not run.

## Templates and UI Copy

- `templates/base.html`: the shell (see Before → After). It links
  `tokens.css` and `style.css` and drops both MUI assets.
- `templates/dashboard.html`: the ledger, the start block, and the tips.
  Metric labels are verbatim from `progress.html:23-39`: 「連續練習天數」
  「作答題數」「掌握題數」「平均得分率」「覆蓋法條數」.
- `templates/law_detail.html`, `quiz_config.html`, `quiz_session.html`,
  `laws.html`, `my_questions.html`, `question_bank.html`, `progress.html`,
  and `login.html`: restyled as above. JS template strings take the new
  class names, and inline color, spacing, and type styles move out.
- `static/img/google-g.svg`: new. It holds the four-color "G" path from
  `login.html:194-197`, unchanged.
- **Copy changes:** emoji section markers dropped, confirmed by the user
  on 2026-10-19:
  - `dashboard.html:24` 「💡 學習小提示」 → 「學習小提示」
  - `law_detail.html:65` 「📝 相關題目」 → 「相關題目」
  - `quiz_session.html:517` 「💡 AI 解析（重點）」 → 「AI 解析（重點）」
  - `quiz_config.html:103` 「💡 說明」 → 「說明」
  - `law_detail.html:38` the 📊 icon before 「次作答」 is removed.
- **Kept as is:** 「⚠️ 載入失敗」, 「📢 回報題目問題」, 「🎉 測驗完成！」,
  「💡 查看解析」, and every emoji on a button.
- **No new copy.**

## LLM Prompts

None — no prompt or model call changes.

## Business Rules and Edge Cases

| ID | Rule or scenario | Expected behavior |
| --- | --- | --- |
| BR-1 | Dashboard range | The five numbers cover all time, for the session's current law type. Switching law type reloads the page (`main.js:130`), and the numbers follow. |
| BR-2 | No records for this user and law type | The ledger shows `0`, `0`, `0`, `0.0%`, `0`. No banner and no new copy. |
| BR-3 | `summary.is_legacy` on `/` | Ignored. The numbers still come from the legacy fallback, and the explanatory banner stays on `/progress` only. |
| BR-4 | Role map | Teal: actions, links, the active tab, the progress fill, 選擇題, 作答題數, and the `--color-data-1` chart. Blue: 法條 (the sheet flag, 覆蓋法條數). Magenta: 簡答題, labeled 問答題 on two pages. Flamingo: 連續練習天數. Neutral: 掌握題數, 平均得分率, and the `--color-data-2` chart. No hue carries two meanings on any page. |
| BR-5 | Status colors | Success, danger, warning, and info appear only for status: score badges, answer review, toasts, alerts, starred items, and the legacy notice. |
| BR-6 | Type | Every element computes to `--font-body`, the 黑體 stack. No Ming face. |
| BR-7 | Shell controls | Every page but login shows the logo, the four nav links, the law-type select, 中/EN, and logout. The user name shows from 1024px. `main.js` still hides 中/EN for law types without EN content, and the shell keeps its layout when it does. |
| BR-8 | Color literals | Only `tokens.css` holds a color literal. `--brand-line`, `--brand-google-border`, and the other `--brand-*` tokens cite the LINE and Google button guidelines. The Google "G" fills live in `static/img/google-g.svg`. |
| BR-9 | Three viewports | Every page passes the `docs/modules/ui/index.md` check at 390x844, 768x1024, and 1440x900. |
| BR-10 | Graded quiz | 「AI 解析（重點）」 has no fill, so the only filled boxes on the result panel are the status ones. |
| BR-11 | Overlays | The modals (z-index 1000–3000) and the loading overlay sit above the shell (z-index 100). The phone tab bar never covers a modal's buttons. |
| BR-12 | Long content | Long law text, long question stems, and long chapter names wrap inside their container. The chapter tabs and index-tab rows scroll sideways inside their own row, never the page. |

## Test Plan

No external calls. Sessions are set with `client.session_transaction()`, as
in `tests/test_auth.py`. Daily stats are seeded into the test database.

- `tests/test_app.py`
  - **Dashboard with stats:** user U, with `user_daily_stats` for
    `patent-act`:
    - yesterday: questions 4, total_score 3.0, laws `["A1", "A2"]`,
      mastered 2;
    - today: questions 8, total_score 6.0, laws `["A2", "A3"]`, mastered 5.

    `GET /` → 200. The body has 「作答題數」 with `12`, `75.0%`
    (9.0 / 12), 「覆蓋法條數」 with `3`, 「掌握題數」 with `5` (the latest
    day's), and 「連續練習天數」 with `2`.
  - **Law type scoping:** the same user with stats only under another law
    type, session on `patent-act` → `GET /` → 200, showing the five
    zeros.
  - **No records (BR-2):** a fresh user id → `GET /` → 200, with
    `0.0%` and no legacy banner text.
  - **Every page in the new shell:** a logged-in session → `GET` on
    `/`, `/laws`, `/laws/<id>`, `/quiz/config`, `/quiz/session/x`,
    `/my-questions`, `/question-bank`, and `/progress` → each 200. Each
    body contains `class="shell"`, `tokens.css`, and the four nav labels,
    and no `muicss`. `GET /auth/login` → 200 with `tokens.css` and no
    `muicss`.
- `tests/test_design_tokens.py` (new)
  - **Contract:** every `--name` declared in
    `.claude/skills/neta-design/tokens/_structure.css` is declared in
    `static/css/tokens.css`.
  - **Literals:** no `#hex`, `rgb(`, `rgba(`, `hsl(`, or `hsla(` in
    `templates/**/*.html`, `static/js/**/*.js`, or `static/css/*.css` other
    than `tokens.css`. This makes the `neta-design` grep part of CI.
  - **Retired files:** `static/css/design-tokens.css` and
    `design-tokens-dark.css` do not exist.

The three-viewport check and the screenshots are the Seen working step,
done in Playwright against `python app.py`, not in `pytest`.

## Rollout and Migration

- No environment variables, config, or data migrations.
- Deploy through the normal CI → Heroku path. Flask serves `static/` with
  revalidation, so a browser picks up the new CSS on its next request.
- Rollback: revert the commit. No data to restore.
- `LP-0002-02`'s artifacts link `static/css/design-tokens*.css`. They stop
  rendering styled once those files are deleted. Their shots remain the
  record, and the onboarding screen is built on `tokens.css` when
  `LP-0002-02` is implemented.

## Implementation Order

Each step leaves `pytest` green and the app usable.

1. **Teal everywhere, nothing broken.**
   - Add `static/css/tokens.css` (`role-hues-teal.css` plus the
     `--brand-*` section) and link it from `base.html` after
     `design-tokens.css`.
   - Re-point `style.css:4-21` at contract names, for example
     `--primary-color: var(--color-accent)` and
     `--border-color: var(--color-border)`.
   - Add the contract test from `tests/test_design_tokens.py`.
2. **Shell.**
   - Rewrite `base.html`'s header as the shell, and drop the MUI CSS and
     JS.
   - Replace `style.css`'s header section (`:49-303`) with the base,
     primitives, and shell rules.
   - Add the every-page shell test.
3. **Dashboard.** The route, the template, and the ledger and start-block
   rules, with the three dashboard tests.
4. **Law detail.** The sheet, index tabs, flags, and the 31 inline styles
   out, with copy changes 2 and 5.
5. **Quiz.** Config, then the session: question, graded with the unfilled
   callout, summary, and modal. Copy changes 3 and 4.
6. **Laws list,** then **my questions** and **question bank**, including
   their JS template strings.
7. **Progress.** The ledger, index-tab range, chart panels, and chart colors
   from tokens.
8. **Login.** Tokens, `--brand-*`, `google-g.svg`, no gradient, and no MUI.
9. **Toasts.** `showToast` sets classes only, and `style.css` colors them.
10. **Retire the bridge.**
    - Delete the alias layer, `design-tokens.css`, and
      `design-tokens-dark.css`.
    - Add the literal and retired-file tests.
    - Run the three-viewport check on every page.
    - Doc sync: `docs/modules/ui/index.md` (the shell replaces "Header by
      range"; the container vocabulary, role map, and token home) and the
      changelog entry.
