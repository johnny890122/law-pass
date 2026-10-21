# dotnet.microsoft.com — spec

- URL: https://dotnet.microsoft.com/en-us/ and https://dotnet.microsoft.com/en-us/learn
- Captured: 2026-10-18
- Scope: the named pages — the homepage (`home`) and the learning hub (`learn`)

## 1. Identification

- **URL:** as above, recorded without the `?utm_source=tailwindcss` referral
  tag the user arrived with. Read on 2026-10-18 for `LP-0004-04`.
- **Kind of site:** the marketing and learning front door of a developer
  platform. The homepage is a long, sectioned product page. The learning hub
  is a topic directory that routes visitors to tutorials, videos, and docs.
- **Why it suits law_pass:** it teaches a large body of material to
  newcomers through bordered topic cards, short descriptions, and one
  obvious next step per block. That is the same job law_pass does for law
  articles and quizzes.
- **Built with:** Tailwind utility classes (`col-span-12`, `md:col-span-12`,
  `gap-8`) on top of a site class layer (`btn`, `card`, `grid-wrapper`,
  `title-1`). Every element carries Tailwind's preflight
  `0px solid rgb(229, 231, 235)` border. The parent-brand header and footer
  are a separate shared component with its own cross-origin stylesheet.

### Capture notes

- Another session held the Playwright MCP browser profile, so a local
  Playwright script drove the same build the MCP server ships (Playwright
  1.62.1, Chromium 1234). It ran the skill's measure snippet verbatim. This
  is the same fallback `LP-0004-01` used.
- A second computed-style pass read what the snippet does not tally: border
  colors, background gradients, text fill, the hover and keyboard-focus
  states of buttons, cards, and links, and a width sweep from 320 to 1600px
  in 4px steps for breakpoints. `tokens.md` marks those rows "supplement".
- The browser emulated the light color scheme, with the `en-US` locale. No
  cookie or consent banner appeared. The page was scrolled once before each
  shot so lazy content rendered.
- Every page is under ten viewports tall, so all six shots are full-page.
  The fixed feedback tab is drawn where the viewport sat. In
  `home-phone.png` and `learn-phone.png` it overlaps card text, and it does
  the same on the live site.

## 2. Screen and section order

### `home`

| # | Section (by function) | What it contains | Notes |
| --- | --- | --- | --- |
| 1 | Parent-brand header and site nav | Parent-brand logo, site name, site nav, live-stream pill, theme toggle, all-products menu, search | Shared header component, not sticky |
| 2 | Hero value statement | Display heading, a large subtitle, a filled primary button beside an outline secondary button, a small platform note | Illustration on the right from 768px. Hidden at 390px |
| 3 | Workload chooser | Centered section heading, four bordered cards (icon, gradient title, one-line description), then a row of eight arrow links to more workloads | Each card border is a different hue |
| 4 | Performance proof | Heading and paragraph with an underlined citation link, beside a chart group: a title and three gauges, each with a value and a label | Gauges are graphics |
| 5 | Promo carousel | Two slides. A slide is a gradient panel with an illustration and an inset white card (heading, text, arrow link). Previous and next, dots, pause | Next slide peeks at the right edge at 768 and 1440 |
| 6 | Two value propositions | Two items, each an illustration, heading, and paragraph | |
| 7 | Learning resources panel | White rounded panel: heading, intro paragraph, primary button, then three resource columns (heading, paragraph, arrow link) | Panel radius 32px |
| 8 | Tooling grid | Centered heading and subtitle, then four columns (heading, paragraph, arrow link) | No cards. Plain columns on the page background |
| 9 | Community panel | White rounded panel: heading with a gradient-text phrase, paragraph, primary button, then three large gradient numerals, each over an underlined label link | Panel radius 12px |
| 10 | Social proof | Two rows of third-party logo tiles in a horizontally scrolling strip with faded edges, beside a heading, paragraph, and arrow link | |
| 11 | Closing call to action | Blue-to-purple gradient band: heading, one line of text, a white button | Radius 32px |
| 12 | Social follow row | Label and seven social-network icons | |
| 13 | Parent-brand footer | Locale select, privacy-choices control, legal links | Gray band |

### `learn`

| # | Section (by function) | What it contains | Notes |
| --- | --- | --- | --- |
| 1 | Parent-brand header and site nav | Same as `home` #1 | |
| 2 | Breadcrumb | Two levels: home link, then current page | Slash separator |
| 3 | Dismissible announcement | Tinted purple banner: icon, bold label, one line of text, small primary button, close control | Rounded 12px, no border |
| 4 | Page title block | Centered gradient-text page title, one bold subtitle line | Magenta and purple radial washes behind the top of the page |
| 5 | Intro media split | Video facade (rounded 20px, play button) beside a heading, two short paragraphs, and an arrow link | |
| 6 | Topic directory | Centered heading, eight bordered topic cards (icon, gradient title, description) | Card border hues cycle through purple, magenta, flamingo, blue |
| 7 | Learning formats | Centered heading, four items (illustration, heading, paragraph, arrow link) | Text centered at 390, left-aligned at 768 and 1440 |
| 8 | Social follow row | Same as `home` #12 | |
| 9 | Parent-brand footer | Same as `home` #13 | |

## 3. Navigation model

- **Placement:** top of the page, white, in two tiers of the same shared
  header: the parent-brand bar and the site's own nav. It is **not sticky**
  (`position: static`) and scrolls away with the page.
- **At 860px and up:** one 54px row with the parent-brand logo, a divider,
  the site name, and seven site-nav items: a product overview menu, a topic
  browse menu, the learning hub, downloads, documentation, community, and
  customer case studies. An overflow menu and an outlined live-stream pill
  follow. On the right sit a theme toggle (icon and label in a pill), an
  all-products menu, and a search icon. Hover and focus underline a nav
  item.
- **Call to action in the bar:** only the outlined live-stream pill. The
  primary actions live in the hero, not the bar.
- **Below 860px, which includes 390 and 768:** two 44px rows, 88px in all.
  Row one has a menu button, a search icon, and the centered parent-brand
  logo. Row two has the site name as a dropdown trigger that holds the site
  nav, with an icon-only theme toggle on the right. 61 header controls are
  hidden at this width, against 48 on desktop.
- **Footer:** parent-brand legal links only. There is no site sitemap
  footer. A social follow row sits above it.

## 4. Layout by viewport

Breakpoints: 540, 845, 860, and 1248px (see `tokens.md`). 390 sits below
all of them, 768 sits between 540 and 845, and 1440 sits above all of them.
No page has horizontal page scroll at any of the three viewports
(`pageScroll: false` measured at each).

| Section / component | 390x844 | 768x1024 | 1440x900 |
| --- | --- | --- | --- |
| Header | Two rows, 88px, menu button | Two rows, 88px, menu button | One row, 54px, full site nav |
| Content container | 10px side padding | 20px side padding | 40px side padding, 1400px max width, centered |
| `home` hero | Text only, left-aligned, buttons side by side | Text left, illustration right, overlapping | Text left, illustration right |
| `home` workload cards | 1 column | 2 columns | 4 columns |
| `home` workload link row | Centered and wrapped, about 2 per row | About 4 per row | One row of 8 |
| `home` performance proof | Text above chart group, three gauges in a row | Text above chart group | Text left, chart group right |
| `home` promo carousel | Illustration panel above, text below with no inset card, arrows on either side of the dots | Gradient panel with inset card left, arrows at both sides, next slide peeking | Same as 768, wider |
| `home` value propositions | 1 column, centered text | 2 columns, left-aligned | 2 columns |
| `home` learning panel | Everything stacked, resources 1 column | Heading left, intro and button right, resources 3 columns | Same as 768, more padding |
| `home` tooling grid | 1 column | 4 columns | 4 columns |
| `home` community panel | Stacked, numerals 1 per row | Heading left, intro right, numerals 2 then 1 | Numerals 3 in a row |
| `home` social proof | Logo strip above text | Logo strip left, text right | Same as 768 |
| `home` closing call to action | Stacked: heading, text, button | Heading left, text and button right | Same as 768 |
| `learn` announcement | Text, then a full-width button below | Text, then a full-width button below | One row: icon, label, text, button, close |
| `learn` intro media split | Video above text | Video left, text right | Video left (max 720px), text right |
| `learn` topic cards | 1 column | 2 columns | 4 columns, 2 rows |
| `learn` learning formats | 1 column, centered | 2 columns, left-aligned | 4 columns |
| Social follow row | Icons wrap to two rows | One row | One row |
| Footer | Centered, stacked | Two rows | One row |
| Feedback tab | Floating pill, bottom-right of the viewport | Floating pill | Vertical tab on the right edge |

## 5. Component inventory

### Bordered topic card

- **Repeats over:** workloads on `home` (4) and topics on `learn` (8).
- **Per row:** 1 at 390, 2 at 768, 4 at 1440.
- **Anatomy:** a whole-card link. A white surface with a 2px colored
  border, 20px radius, 20px padding, and a faint shadow. Inside: a small
  line icon, a title set as gradient text in the card's hue, and a 1–3 line
  description. Hues cycle per card: purple, magenta, blue, and flamingo on
  `learn`.
- **Interaction:** hover turns the surface light gray and deepens the
  shadow. Keyboard focus draws a 1px dashed outline. Static CSS.

### Buttons

- **Primary:** filled accent, white text, 2px border in the fill color, 8px
  radius, `12px 20px` padding, 52px tall. Hover darkens the fill. Focus
  draws a 1px black outline at a 2px offset. A small variant in the
  announcement banner uses 6px padding and 14px text.
- **Outline (secondary):** transparent fill, accent text and 2px accent
  border. Hover fills it with a pale accent tint. Sits beside the primary
  button in the hero.
- **Inverse:** white fill and border, accent text. Used only on the
  gradient call-to-action band.

### Arrow link

- **Repeats over:** every "go deeper" action under a column, card, or
  panel.
- **Anatomy:** accent text in 600 weight, followed by a right-arrow glyph.
  No underline at rest.
- **Interaction:** hover darkens the text and underlines it. Focus draws a
  1px dashed outline.

### Rounded panel

- **Repeats over:** the learning panel and the community panel on `home`.
- **Anatomy:** a white surface on the near-white page, with no border or
  shadow. Radius is 32px for the learning panel and 12px for the community
  panel. Padding grows by width: `20px 24px`, then `28px 48px`, then
  `80px 108px`.

### Stat block

- **Repeats over:** three community numbers.
- **Per row:** 1 at 390, 2 then 1 at 768, 3 at 1440.
- **Anatomy:** a very large display numeral in gradient text over an
  underlined label link.

### Announcement banner

- **Repeats over:** one per page, on `learn`.
- **Anatomy:** a tinted accent surface, 12px radius, no border. A small
  gradient icon sits in the left padding, then a bold label, a line of
  text, a small primary button, and a close control. The button drops
  below the text and goes full-width below 1440 in the shots.
- **Interaction:** the close control dismisses it.

### Breadcrumb

- Two levels, 14px, a slash separator, and a dark link followed by muted
  current-page text. Sits under the header with no background.

### Section heading block

- A centered display heading, sometimes with a one-line subtitle, opens
  most sections. Item titles inside a section use the content face at
  600 weight.

### Promo carousel

- Two slides with previous and next arrows, dot indicators (12px circles,
  filled when current), and a pause control. It rotates on its own.

### Media split

- A video facade on one side and text on the other. The video loads only
  when its play button is clicked.

### Illustrated feature item

- A large illustration over a heading, a paragraph, and an arrow link.
  Repeats as `home` value propositions (2) and `learn` learning formats
  (4).

### Logo strip

- Two rows of white rounded tiles holding third-party logos, with faded
  gradient edges, scrolling sideways inside its column.

### Theme toggle

- A pill with a 1px dark border and a 999px radius. It shows an icon and a
  label on desktop, and only the icon below 860px.

### Feedback tab

- A fixed control in the accent fill. It is vertical on the right edge at
  1440 and a floating pill at 390 and 768.

## 6. Interaction inventory

| Interaction | What it does | static ok / needs JS / needs server |
| --- | --- | --- |
| Site nav dropdowns (product overview, topic browse, overflow) | Open sub-menus on desktop | needs JS |
| Site-name dropdown (below 860px) | Holds the site nav on phone and tablet | needs JS |
| Menu button (below 860px) | Opens the parent-brand menu | needs JS |
| Search icon | Opens site search | needs JS, needs server |
| Theme toggle | Switches light and dark themes. Only light was captured | needs JS |
| Card hover and focus | Gray surface and deeper shadow, dashed focus outline | static ok |
| Button hover and focus | Darker fill or tinted fill, solid focus outline | static ok |
| Arrow-link and nav hover | Underline, darker text | static ok |
| Promo carousel | Auto-rotates, with previous, next, dots, and pause | needs JS |
| Logo strip | Scrolls sideways within faded edges. Whether it auto-scrolls was not observed | needs JS |
| Announcement close | Dismisses the banner | needs JS |
| Video facade | Swaps the thumbnail for an embedded player on click | needs JS, needs server |
| Feedback tab | Opens a feedback form. Not opened | needs JS, needs server |
| Locale select | Reloads the site in another locale | needs server |
| Privacy-choices control | Opens privacy settings | needs server |
| Breadcrumb and plain links | Navigate | static ok |

## 7. Do not reproduce

`neta-design` keeps every item below off every variant:

- **Logos and wordmarks:** the parent-brand four-square logo and wordmark,
  and the site name used as a logo in the header.
- **Mascots:** the purple robot characters in the promo carousel.
- **Illustrations:** the isometric device art in the hero, the globe, the
  monitor-and-devices art, the cubes, the magnifier, the database-and-book
  art, and the carousel's rocket and space art.
- **Photography:** the presenter photo inside the video thumbnail.
- **Charts as art:** the three benchmark gauges.
- **Third-party logos:** every customer logo in the social-proof strip and
  every social-network icon.
- **Icon sets:** the parent brand's icon font and the line icons on the
  topic cards.
- **Fonts as files:** the parent brand's web-served UI font. `tokens.md`
  records family names only. No font file is copied.
- **Signature motifs:**
  - gradient text on titles and numerals
  - the magenta and purple radial washes behind the page top
  - the blue-to-purple gradient band and gradient promo panel
  - the per-card hue rotation of borders and title gradients
- **All copy:** headlines, taglines, body text, nav labels, button labels,
  and statistics.

The accent purple is not on this list. Per `LP-0004`, it is a token, and
`tokens.md` records it as a color role.
