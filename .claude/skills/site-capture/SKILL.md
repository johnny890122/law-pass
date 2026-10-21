---
name: site-capture
description: "Capture an external reference site into `docs/references/<site-slug>/`: a dated written spec of its screens, navigation, layout at phone, tablet, and desktop, components, and interactions, plus measured tokens and committed screenshots, so `neta-design` can derive a design system without reopening the site. Use when the user names a reference site to learn from, or a ticket calls for a capture. Never for capturing law_pass itself."
---

# Site Capture

Produces the durable record of an **external reference site** that
[`neta-design`](../neta-design/SKILL.md) derives token values and layouts
from. The record lives in `docs/references/<site-slug>/`, as `CLAUDE.md`'s
doc tree lists. If `neta-design` has to reopen the live site, the capture
failed.

## Trigger Gate

Proceed only when one of these holds:

- The user names a reference site to learn from.
- A ticket calls for a capture, such as `LP-0004-04`.

Never capture law_pass itself. The app's current state is `templates/` and
`static/css/`, and its layout is checked by the done gate, not recorded
here. If the user asks to capture law_pass, say so and stop.

## 1. Confirm

Before opening the site, confirm two things with AskUserQuestion:

- **The URL**, exactly as it will be recorded.
- **The scope**: the homepage only, or a named list of pages. Capture
  nothing outside it, with no crawling and no following links to find more.

Pick the `<site-slug>` from the domain in kebab-case, such as
`law-moj-gov-tw`, and say it in the same message. If
`docs/references/<site-slug>/` already exists, this is a re-capture: delete
the folder and write it fresh. Git keeps the old one.

Read the site as a visitor would. Do not log in, submit forms, or accept
anything beyond what is needed to see the page.

## 2. Measure

Use Playwright MCP for each page in scope, at **390x844**, then
**768x1024**, then **1440x900**:

1. `browser_resize`, then `browser_navigate` to the page. Dismiss a cookie
   banner only if it covers the layout, and note that in `spec.md`.
2. `browser_evaluate` the script below. Keep each result in the session
   scratchpad, keyed by page and viewport. These values are the only source
   for `tokens.md`. Never read a value off a screenshot.
3. `browser_take_screenshot` with `fullPage: true` to
   `docs/references/<site-slug>/shots/<page>-phone.png`, `-tablet.png`, or
   `-desktop.png`. `<page>` is `home` or the page's function in kebab-case.
   If the page is more than about ten viewports tall, shoot the first
   viewport only and say so in `spec.md`. Then read the saved PNG and look
   at it.
4. Use `browser_snapshot` and the screenshot to record the section order,
   navigation, and how the layout changes. Note what each section is *for*,
   not what it says.

```js
() => {
  const name = e => e.tagName.toLowerCase()
    + (e.id ? '#' + e.id : '')
    + (typeof e.className === 'string' && e.className.trim()
      ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const shown = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const els = [...document.querySelectorAll('body *')].filter(shown);
  const tally = (prop, skip = []) => {
    const m = {};
    for (const e of els) {
      const v = getComputedStyle(e)[prop];
      if (v && !skip.includes(v)) (m[v] ??= { count: 0, first: name(e) }).count++;
    }
    return Object.entries(m).sort((a, b) => b[1].count - a[1].count).slice(0, 12)
      .map(([value, { count, first }]) => ({ value, count, first }));
  };
  const pick = sel => [...document.querySelectorAll(sel)].filter(shown).slice(0, 3).map(e => {
    const s = getComputedStyle(e);
    return { el: name(e), color: s.color, bg: s.backgroundColor, font: s.fontFamily,
      size: s.fontSize, weight: s.fontWeight, line: s.lineHeight, padding: s.padding,
      radius: s.borderRadius, border: s.border, shadow: s.boxShadow, max: s.maxWidth };
  });
  const media = new Set();
  for (const sheet of document.styleSheets) {
    try { for (const r of sheet.cssRules) if (r.media) media.add(r.media.mediaText); }
    catch { media.add('cross-origin: ' + sheet.href); }
  }
  return {
    viewport: innerWidth + 'x' + innerHeight,
    pageScroll: document.documentElement.scrollWidth > innerWidth,
    container: pick('main, [class*=container]'), body: pick('body'), headings: pick('h1, h2, h3'), links: pick('a'),
    buttons: pick('button, [role=button], a[class*=btn], a[class*=button]'),
    fields: pick('input, select, textarea'), chrome: pick('header, nav, footer'),
    colors: tally('color'), backgrounds: tally('backgroundColor', ['rgba(0, 0, 0, 0)']),
    families: tally('fontFamily'), sizes: tally('fontSize'),
    padding: tally('padding', ['0px']), gap: tally('gap', ['normal']),
    radius: tally('borderRadius', ['0px']), shadows: tally('boxShadow', ['none']),
    media: [...media],
  };
}
```

Each `tally` row names the first element that carries the value, so every
token stays traceable. A stylesheet listed as `cross-origin` hides its media
queries. In that case, find the breakpoints by resizing between the three
viewports until the layout changes, and record them as "observed".

## 3. Write

Both files open with the same header, titled `— spec` or `— tokens`:

```markdown
# <Site name> — spec

- URL: <url>
- Captured: YYYY-MM-DD
- Scope: <homepage only | the named pages>
```

### `spec.md`

Write these sections, in this order:

1. **Identification**: the URL, the date read, what kind of site it is, and
   one sentence on why it suits a law-exam quiz app.
2. **Screen and section order**: one numbered table per page, top to bottom,
   with one row per section, named by **function** ("primary call to
   action", "progress summary"), never by its headline.
   `| # | Section (by function) | What it contains | Notes |`
3. **Navigation model**: placement, whether it is sticky, how many items
   (named by function), whether a call to action sits in the bar, and what
   it becomes at phone width.
4. **Layout by viewport**: what reflows, collapses, or hides at 390x844,
   768x1024, and 1440x900, as a table with one row per section or component.
   Note any horizontal page scroll you measure.
5. **Component inventory**: one subsection per recurring component, such as
   card, list row, tab set, form field, or badge. Give what it repeats over,
   how many per row at each viewport, its anatomy, and its interaction.
6. **Interaction inventory**:
   `| Interaction | What it does | static ok / needs JS / needs server |`
7. **Do not reproduce**: logos, wordmarks, mascots, illustrations,
   photography, icon sets, signature motifs, and all copy. List each one the
   site has. `neta-design` keeps every item off every variant.

### `tokens.md`

One table per group: color roles, type families, type scale, spacing scale,
radius, shadow, and breakpoints.

`| Role | Value | Element | Viewport |`

- **Role** names what the value does on the site ("page background", "muted
  text", "primary button fill"), so `neta-design` can map it onto
  `tokens/_structure.css`.
- **Value** is the computed value as measured, such as `rgb(31, 78, 121)` or
  `16px`.
- **Element** is the `el` or `first` name from the script, and **Viewport**
  is the size it was read at. A value that holds at all three says `all`.
- Record what the site has, not what law_pass needs. A role the site does
  not render is left out, not guessed.

## Rules

- **Descriptive only.** Record what the site is, including what is broken.
  Opinions and proposals belong in the ticket that uses the capture.
- **Re-capture, never patch.** If the site changed or the capture is wrong,
  redo the folder with a new date.
- **No assets.** Download or commit nothing from the site: no image, font,
  icon, SVG, or stylesheet. Screenshots are the only images kept.
- **No copy.** Carry no headline, tagline, body text, or nav label from the
  reference into either file. Name things by function.

## 4. Output Check

The capture is done when `neta-design` can derive a token file and a layout
from `docs/references/<site-slug>/` alone, without opening the live site.
Before handing it off:

- Read `spec.md` and `tokens.md` cold, and confirm a layout for each section
  could be built at all three viewports from them.
- Every `tokens.md` row names an element and a viewport.
- `shots/` holds `-phone`, `-tablet`, and `-desktop` for every page in
  scope, and nothing else is in the folder besides the two `.md` files.
- Neither file quotes the site's copy.

Then give the user the folder path, the page count, and the do-not-reproduce
list.
