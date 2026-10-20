# UI

How every page looks and holds across screen sizes. The look is the
`dense-tabbar` layout with the teal `role-hues` palette, adopted on every page
by [LP-0004-07](../../changelog/2026-10-20-adopt-design-system.md). The
viewport rules date from
[LP-0004-03](../../changelog/2026-10-18-rwd-all-pages.md).

## Product rules

### Holding across screen sizes

- **Three viewports.** Every page holds at phone 390x844, tablet 768x1024,
  and desktop 1440x900. Learners study on phones first, so phone is the
  primary check.
- **"Holds" means:** no horizontal page scroll, no element whose content
  spills past its box, no nav link wrapping or clipped, long law text and
  explanations wrapping inside their container, and charts filling their
  panel. The automated part is this `browser_evaluate`, run on every page at
  each viewport. `pageScroll` must be false and `overflowing` empty:

  ```js
  () => ({
    pageScroll: document.documentElement.scrollWidth > innerWidth,
    overflowing: [...document.querySelectorAll('body *')]
      .filter(e => e.clientWidth && e.scrollWidth > e.clientWidth + 1
        && getComputedStyle(e).overflowX === 'visible')
      .map(e => e.tagName + '.' + e.className),
  })
  ```

  Then look at the screenshot. The check cannot see a word wrapping inside a
  button or a nav link.
- **Mobile-first, two breakpoints.** Base rules in `style.css` are the phone
  layout. `@media (min-width: 768px)` adds tablet and up, and
  `@media (min-width: 1024px)` adds desktop. No `max-width` media queries
  and no other breakpoints.
- **Rows of tabs scroll sideways inside themselves**, never the page: the
  chapter tabs on `/laws` and every index-tab row.

### The shell

One markup in `base.html`, two arrangements, on every page but login:

| Width | Layout |
| --- | --- |
| Below 1024px | A sticky top bar (logo, the law-type select taking the free width, 中/EN, logout) and a fixed bottom tab bar of the four nav links. The active tab is marked on its top edge. The user name is hidden. The body pads the tab bar plus `env(safe-area-inset-bottom)`. |
| 1024px and up | A fixed left sidebar: logo, select, the four links stacked (the active one on an accent tint), then 中/EN and the user name with logout at the bottom. |

- Every control stays at every width: logo, 首頁 法條瀏覽 題庫 我的進度, the
  law-type select, 中/EN, and logout. The user name shows from 1024px.
- The active link comes from `request.path`: `/` is 首頁, `/laws*` 法條瀏覽,
  `/question-bank` 題庫, `/progress` 我的進度. Other pages mark none.
- **The language toggle shows only for patent-act**, the one law type with EN
  content. `main.js` hides it for the others, and the shell keeps its layout.
- **Stacking:** the shell is z-index 100, toasts 1000, the loading overlay
  2000, and modals 3000. A modal always covers the tab bar, and toasts sit
  above the tab bar on phone.

### Tokens and type

- **One token file.** `static/css/tokens.css` holds every token value and is
  the only file allowed a color literal. `style.css`, the templates, and JS
  read token names only. `tests/test_design_tokens.py` fails on a `#hex`,
  `rgb(a)(`, or `hsl(a)(` anywhere else in `templates/`, `static/js/`, or
  `static/css/`.
- Its names follow the contract in
  `.claude/skills/neta-design/tokens/_structure.css`, plus the `--d-*`
  direction tokens and `--brand-*` marks. It started as a copy of
  `role-hues-teal.css` (the `LP-0004-08` winner) and is now the source of
  truth. The skill's copy is a record and is not kept in sync.
- **`--brand-*` tokens** are Google's and LINE's own button values, used only
  on the login page's two sign-in buttons. They are never a law_pass role.
  The Google "G" keeps its four colors inside `static/img/google-g.svg`.
- **All text is 黑體** (`--font-body`), including law text. No Ming face and
  no web font.
- Charts read `--color-data-1` and `--color-data-2` through
  `getComputedStyle`. Both stay plain `#rrggbb`, because the chart code adds
  alpha as a hex suffix.

### Containers

One container per role, so a learner can tell what kind of thing they are
looking at:

| Container | Class | Used for |
| --- | --- | --- |
| Ledger | `.metrics` / `.metric` | Numbers on rules, no box: the five progress numbers on `/` and `/progress`, and the quiz summary. A list on phone (label left, number right). One row from 768px. |
| Panel | `.card` | A white box with light lines: the question, the graded result, every question list, the quiz form, the chart blocks, and the pager. |
| Sheet | `.law-panel` | The law article, with `--radius-sm` corners and the 法條 flag on its top edge. Sticky on the left from 1024px. |
| Ruled list | `.tips`, `.question-list`, `.law-list` | Rows split by rules, never a card per item: tips, 說明, related questions, my questions, the question bank, and the laws list. |
| Index tabs | `.filter-tabs` / `.filter-tab` | Every filter or range switch. They sit on a rule, and the active tab is open at the bottom. Inside a panel the rule bleeds to the panel's edges. At page level it sits flush with the content. |

The dashboard and `/progress` share one ledger partial,
`templates/_ledger.html`.

### Role map

Each hue means one thing on every page. Hues are solid marks (badges, flag
keys, the sheet flag), held to 3:1 as graphics. Text stays ink, except
actions and links.

| Hue | Token | Means |
| --- | --- | --- |
| Teal | `--color-accent` | Actions, links, the active tab, the progress fill, 選擇題, 作答題數, and the `--color-data-1` chart |
| Blue | `--d-flag-law` | 法條: the sheet flag and 覆蓋法條數 |
| Magenta | `--d-flag-short` | 簡答題, labeled 問答題 on my questions and the question bank |
| Flamingo | `--d-flag-streak` | 連續練習天數 |
| Neutral | text and border tokens | 掌握題數, 平均得分率, and the `--color-data-2` chart |

- An element gets a flag key from `data-flag="accent|short|law|streak"`. An
  empty `data-flag` keeps the key's space so ledger labels line up. Keys are
  tied to meaning, not position.
- **Status colors are only status.** Success, danger, warning, and info mark
  score badges, answer review, toasts, alerts, starred items, modal warnings,
  and the legacy notice on `/progress`.
- **The graded quiz keeps teal and success apart.** 「AI 解析（重點）」 has
  no fill: a rule above it and its label in teal. The only filled boxes on
  the result panel are status ones.
- **No emoji section markers.** Headings carry no emoji. Emoji on buttons and
  in titles such as 「🎉 測驗完成！」 stay.

### Pages

- **`/`** opens on the ledger, with numbers for all time and the session's law
  type. A learner with no records sees `0 0 0 0.0% 0` and no banner. Under
  the ledger come 開始新測驗 at full width, then 法條瀏覽 and 我的題目 side by
  side, then the tips. From 1024px the ledger spans the top, with the start
  block and the tips side by side under it.
- **Charts** on `/progress` keep Chart.js's 2:1 shape, capped at 260px tall,
  and always span their panel. They sit side by side from 1024px.
- **Login** has no shell: one panel centered on `--color-bg`.
- **Shared layout lives in `style.css`.** A template's `style=` may only
  toggle state, such as `display: none` or a progress `width`. Color,
  spacing, and type are classes.

## Code

- `static/css/tokens.css`: every token value.
- `static/css/style.css`: base and primitives, the shell and containers, the
  flags, then one section per page. Both breakpoint blocks sit at the end.
- `templates/base.html`: the shell markup. `templates/_ledger.html`: the five
  progress numbers.
- `routes/frontend.py`: `/` loads `get_progress_summary(user, None, law_type)`.
- `templates/progress.html`: Chart.js options and token colors.
- `static/js/main.js`: language toggle visibility by law type, and
  `showToast`, which sets classes only.
