# LP-0004-05 · Decision

**Question:** what does law_pass look like, as a system, on the dashboard,
the quiz session (question and graded), and law detail?

## Winner: `dense-tabbar`, layout only

The `dense-tabbar` direction (`dense-tabbar-*.html`, `dense-tabbar-layout.css`)
wins on **layout**. Its thesis: a study app. On phone a bottom tab bar holds
the four nav links and a one-row top bar holds the law-type select, 中/EN,
and the user menu. On desktop the nav becomes a left sidebar. The dashboard
opens on the five progress numbers with 開始新測驗 under them. It is dense
enough that a whole question and its options fit one phone screen.

**Color is not decided here.** The user likes the layout but wants the colors
to read like the dotnet.microsoft.com example, which `dense-tabbar` does not
yet do. Its values file keeps only the capture's neutrals and puts purple on
buttons and active states, so it reads gray. `LP-0004-06` builds three color
variants on this layout and picks the palette.

From `.claude/skills/neta-design/tokens/dense-tabbar.css`, these carry
forward unchanged: type (sizes, weights, leading, faces), space, radius,
elevation, focus ring, motion, and the `--d-bar-height` and
`--d-sidebar-width` tokens. The `--color-*` roles and `--border-width` are
reopened by `LP-0004-06`.

## Rejected

- **`baseline`**: today's layout with the dotnet values. It changes nothing
  a learner would notice. The desktop dashboard stays three full-width
  buttons, and law text runs about 70 characters a line at 1440.
- **`reading-room`**: one quiet header row, chapters first, law text and
  question stems set as a serif document. Generous whitespace makes pages
  long, and on phone the nav, 中/EN, and the user menu sit one tap away
  behind a menu.

## What the real implementation must keep

- **One shell markup, two arrangements.** Below 1024px: a sticky top bar
  (logo, law-type select taking the free width, 中/EN, logout) and a fixed
  bottom tab bar of four text-only tabs, the active one in an accent pill.
  The user name is hidden. From 1024px the same shell is a fixed left
  sidebar: logo, select, the four links stacked, then 中/EN and the user
  name with logout pinned to the bottom. Body padding clears the tab bar
  plus `env(safe-area-inset-bottom)`.
- **Every `base.html` control and label stays**: logo, 首頁 法條瀏覽 題庫
  我的進度, the law-type select, 中/EN, the user name, and logout.
- **Dashboard order**: the five `progress.html` metrics in one strip
  (連續練習天數, 作答題數, 掌握題數, 平均得分率, 覆蓋法條數), then 開始新測驗
  full width, then 法條瀏覽 and 我的題目 side by side, then 💡 學習小提示.
  On phone the strip is five columns. Labels break only at word boundaries
  (`<wbr>` with `word-break: keep-all`), and values step down to `--text-lg`.
  From 1024px the strip spans the top, with the start block and the tips
  side by side under it.
- **Quiz**: progress is one row (題目進度, bar, 3 / 10). The question card
  holds the badge and 第 N 題 on one line, then the stem, then the options.
  At 390x844 the card ends well above the tab bar. The graded card puts ☆,
  📢, and 下一題 in one row, with 下一題 taking the remaining width.
- **Law detail**: ← 返回法條列表 is a text link. The law panel holds 第 N 條
  with the chapter, attempts, and average on one meta line, and the star
  button. Law text stays UI, with hanging paragraph numbers. On phone the
  filter tabs scroll sideways in one row. From 1024px the page is two
  columns, with the law panel sticky on the left and 相關題目 on the right.
- **The system tier holds.** `system.css` (reset, focus ring, primitives)
  needed no direction-specific edit across all three directions, and its
  class names follow `static/css/style.css`.
- **Carry-forward for adoption:** `/` renders `dashboard.html` with no data
  today (`routes/frontend.py`). The metric strip needs
  `get_progress_summary` (`services/progress.py`), which only `/progress`
  calls. That makes adoption a route change, not only a template one, and
  the strip's time range still has to be chosen.

Stand-ins in the mock: the user name 王小明, the five progress numbers, the
question and its options, the AI explanation, the related-question counts,
and the attempt count and average. Article 22's text and the chapter names
are verbatim from `knowledge/patent_law_zh.md`.

## Who decided, on what evidence

Johnny Chang picked the `dense-tabbar` layout on 2026-10-19, after the review
of the 36 shots in `shots/` (phone first), plus
`reading-room-dashboard-phone-menu-open.png`. The same review sent color to a
follow-up ticket, `LP-0004-06`, and asked for three color variants on this
layout.
