# UI

How every page holds across screen sizes. Current truth since
[LP-0004-03](../../changelog/2026-10-18-rwd-all-pages.md). Tokens and the
look itself are out of scope here until LP-0004-06 adopts a design system.

## Product rules

- **Three viewports.** Every page holds at phone 390x844, tablet 768x1024,
  and desktop 1440x900. Learners study on phones first, so phone is the
  primary check.
- **"Holds" means:** no horizontal page scroll, no element whose content
  spills past its box, no nav link wrapping or clipped, long law text and
  explanations wrapping inside their card, and charts filling their card.
  The automated part is this `browser_evaluate`, run on every page at each
  viewport. `pageScroll` must be false and `overflowing` empty:

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
- **Header by range:**

  | Width | Layout |
  | --- | --- |
  | Below 768px | Two rows: logo, then language toggle and logout. Below that, nav links (scroll sideways if needed) and the law type select. User name hidden. |
  | 768–1023px | One row. Nav links never wrap. User name hidden, so the row fits at 768px with about 25px to spare. |
  | 1024px and up | One row with the user name. |

- **Language toggle shows only for patent-act**, the one law type with EN
  content. `main.js` hides it for the others at every width.
- **Charts** on the progress page keep Chart.js's 2:1 shape, capped at 260px
  tall, and always span their card.
- **Shared layout lives in `style.css`.** A layout pattern used by more than
  one page (for example the `.pager` prev/page/next card) is a class, not a
  copied inline `style=`. One-off cosmetic inline styles may stay.

## Code

- `static/css/style.css`: all layout rules and both breakpoints.
- `templates/base.html`: the header markup.
- `templates/progress.html`: Chart.js options (`maintainAspectRatio: false`,
  sized by `.chart-container`).
- `static/js/main.js`: language toggle visibility by law type.
