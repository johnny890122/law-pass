# 2026-10-18 — Every page holds at phone, tablet, and desktop

**LP ids:** LP-0004-03

The layout had only ever been checked at phone and desktop, and `style.css`
mixed four breakpoint styles. An audit of every page at 390x844, 768x1024,
and 1440x900 found no page scroll and no overflowing element. Looking at the
screenshots found three defects: the tablet nav wrapping, the progress
charts not filling their cards, and the pager buttons squeezing on phone.
The CSS is now mobile-first with two breakpoints. Rules live in
[`docs/modules/ui/index.md`](../modules/ui/index.md).

| Area | Was | Now |
| --- | --- | --- |
| Breakpoints | `max-width: 640px` (twice), `max-width: 767px`, `min-width: 768px` (three times), `min-width: 1024px`. | Phone rules are the base. Only `min-width: 768px` and `min-width: 1024px`. A computed-style diff against the old CSS showed every page identical at phone, and identical outside the header at tablet and desktop, apart from the fixes below. |
| Header, 768–1023px | One row. Every nav link broke onto two lines (「首/頁」, 「法條/瀏覽」), making the header 100px tall. | One row, links on one line, user name hidden. The header is 75px tall. |
| Header, 641–767px | One-row desktop header, squeezed. | The phone two-row header. Not one of the three audited viewports. |
| Language toggle on phone | Forced visible by a phone-only `!important`, even for law types with no EN content. | Follows `main.js` at every width: shown only for patent-act. |
| Progress charts, tablet and desktop | Drawn 520px wide inside 702px (tablet) and 834px (desktop) cards. | Fill the card, 260px tall. Phone unchanged at 324x162. |
| Pager on 題庫 and 我的題目, phone | Inline flex row. 「← 上一頁」 broke onto two lines. | Shared `.pager` class in `style.css`. Buttons stay on one line, and the page count wraps in the middle. |
| `CLAUDE.md` done gate item 3 | "Seen working" with no viewport named. | A template or CSS change is seen at all three viewports and passes the UI check. |

## Deliberately not done

- Moving the other inline `style=` attributes (31 in `law_detail.html`).
  None broke layout at any viewport. They are cosmetic, and LP-0004-06
  rewrites the templates anyway.
- Removing duplicate rules in `style.css` (`.spinner`, `@keyframes spin`,
  `.empty-state` are each defined twice). Not a layout defect.
- Short-answer graded feedback was not audited. Grading needs OpenRouter,
  which is unset locally. The short-answer question state was audited.
- Token changes, restyling, other breakpoints, and dark mode.
