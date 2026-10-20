# 2026-10-20 — The teal dense-tabbar design system on every page

**LP ids:** LP-0004-07

The user picked the look in three steps: the `dense-tabbar` layout
(LP-0004-05), the `role-hues` palette and frame (LP-0004-06), and teal as the
main color (LP-0004-08). This landing puts it in the real app, on every page
at once, per the approved
[PRD](../prd/LP-0004-07-adopt-design-system.md). Rules now live in
[`docs/modules/ui/index.md`](../modules/ui/index.md).

| Area | Was | Now |
| --- | --- | --- |
| Stylesheets | MUI 0.10.3 CSS and JS from a CDN, the Figma `design-tokens.css`, and a 2,223-line `style.css` that aliased 15 legacy names and held 28 color literals. | `tokens.css` (the teal values file, plus `--brand-*` for the Google and LINE buttons) and a rewritten `style.css` that reads token names only. No MUI. `design-tokens.css` and `design-tokens-dark.css` are deleted. |
| Color literals | 28 in `style.css`, 28 in `login.html`, more in the list pages' inline `<style>` blocks, the Chart.js options, and `showToast`. | Only in `tokens.css`, enforced by `tests/test_design_tokens.py`. The Google "G" colors live in `static/img/google-g.svg`. |
| Header | Sticky, two rows on phone, one row from 768px. | The shell: a top bar plus a bottom tab bar below 1024px, and a left sidebar from 1024px. Every control and `id` kept. |
| `/` | Three buttons and tips, with no data. | The five all-time progress numbers for the current law type as a ledger, then 開始新測驗, 法條瀏覽 and 我的題目, then the tips. A learner with no records sees zeros. |
| Containers | A shadowed card for everything, and pills for filters. | Ledger, panel, sheet, ruled list, and index tabs, one per role. |
| Hues | One primary blue for everything. 簡答題 borrowed the warning amber. | Flags with fixed meanings: teal for actions, 選擇題, and 作答題數; blue for 法條; magenta for 簡答題 (問答題); flamingo for the streak. Status colors are only status. |
| Graded quiz | 「💡 AI 解析（重點）」 in a box with a primary outline. | 「AI 解析（重點）」 with no fill: a rule above it and a teal label, so the green answer box is the only tint near it. 下一題 sits in the action row. |
| Progress charts | Literal indigo bars and a green line. | Teal bars (`--color-data-1`) and a neutral line (`--color-data-2`), read from tokens. Axis text uses the 黑體 stack. |
| Login | A purple gradient page with MUI. | One panel on `--color-bg`, on the shared stylesheets. The Google and LINE buttons keep their owners' colors. |
| Toasts | Literal colors set in `style.cssText`. | `showToast` sets classes only, and `style.css` colors them from the status pairs. They sit above the tab bar. |
| Type | System stack, with law text in the same face. | 黑體 everywhere (`--font-body`), checked by script on every page at three viewports. |
| Copy | | Emoji section markers dropped: 「學習小提示」, 「相關題目」, 「AI 解析（重點）」, 「說明」, and the 📊 in law detail's meta line. |

Checked in the running app on a throwaway copy of the dev database: 17 pages
and states at 390x844, 768x1024, and 1440x900. The run found no page scroll,
no overflowing element, one font family everywhere, and no HTTP or script
errors. The screenshots were looked at. `pytest` (116) and `flake8` pass.

## Implementation notes

- **Build order.** The PRD's step 1 (re-point the alias layer as a bridge) was
  skipped. `style.css` was rewritten in one pass, so there was nothing to
  bridge.
- **Flags by meaning.** Flag keys come from a `data-flag` attribute, not from
  the reference CSS's `:nth-child` positions. My questions has a 收藏 / 答錯
  tab row that position-based keys would have colored wrongly.
- **List badges.** On my questions and the question bank, the score badges are
  the shared `badge-success`, `badge-danger`, and `badge-count`. The status
  colors are kept, and the per-page inline `<style>` blocks are gone.
- **Laws list.** The search field sits above one panel that holds the chapter
  index tabs and the ruled list. Each row's text is clamped to three lines.
  The chapter tabs are now `<button>`s, so they take keyboard focus.
- **Fixed in passing:**
  - On law detail, clicking the count inside a filter tab set the filter to
    `undefined` and emptied the list. The handler now reads `currentTarget`.
  - The law detail error title read an undefined `--error-color`.
  - The law detail loading text was white on white.
- **Kept as is:** 「📚 章節篩選」 and 「📑 全部」 on the laws list (not in the
  PRD's copy list), the 👤 on login (now on a neutral circle), and the type
  emoji in list badges.
- **New accessible names**, with no visible copy: the search clear button is
  labeled 「清除搜尋」, the ledger section is labeled 「我的進度」 as in the
  mock, and toasts carry `role="status"`.

## Deliberately not done

- Dark mode. No ticket yet.
- Hanging paragraph numbers in law text, as in the mock. Law content arrives
  as one string, and splitting it is a data question.
- The quiz summary still shows the progress row from the last question. That
  was true before.
- LP-0002-02's artifacts link the deleted `design-tokens*.css` and now render
  unstyled. Their shots remain the record. Its draft PRD gives the account
  link `class="btn-logout"`, which in the new shell hovers red. That PRD needs
  a pass before approval.
