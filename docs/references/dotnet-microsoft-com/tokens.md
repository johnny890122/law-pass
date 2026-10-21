# dotnet.microsoft.com — tokens

- URL: https://dotnet.microsoft.com/en-us/ and https://dotnet.microsoft.com/en-us/learn
- Captured: 2026-10-18
- Scope: the named pages — the homepage (`home`) and the learning hub (`learn`)

Values are computed styles, read in the light color scheme. Rows without a
note come from the `site-capture` measure snippet. Rows marked
**supplement** come from a second computed-style pass for what the
snippet does not tally: border colors, gradients, text fill, hover and
focus states, and a width sweep. See `spec.md`, "Capture notes". **Viewport**
`all` means the value held at 390x844, 768x1024, and 1440x900. Element
names are `tag#id.class` as the script prints them.

## Color roles

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Page background | `rgb(250, 250, 250)` | `body.refresh.ms-Fabric` | all |
| Surface: header, cards, panels | `rgb(255, 255, 255)` | `header.uhf-header`, `a.card.purple-primary`, `section.grid-wrapper.grid-card` | all |
| Card hover surface (supplement) | `rgb(245, 245, 245)` | `a.card` on hover | all |
| Footer band | `rgb(235, 235, 235)` | `div.footer-wrapper` | all |
| Accent: primary button fill, link text, outline-button text and border, feedback tab | `rgb(81, 43, 212)` | `a.btn.btn-primary`, `a.arrow-link`, `a.btn.btn-default` | all |
| Accent hover: primary button fill, link text (supplement) | `rgb(65, 34, 170)` | `a.btn.btn-primary` on hover, `a.arrow-link` on hover | all |
| Accent tint: outline-button hover fill (supplement) | `rgb(238, 234, 251)` | `a.btn.btn-default` on hover | all |
| Accent tint, stronger: announcement surface | `rgb(220, 213, 246)` | `div.alert-promo.alert` | all (`learn`) |
| Text on accent | `rgb(255, 255, 255)` | `a.btn.btn-primary` | all |
| Text on gradient band | `rgb(245, 245, 245)` | `section.get-started.get-started-blue` | all |
| Hero heading and platform note: deep accent | `rgb(25, 6, 73)` | `h1.display-2.title`, `p.caption-1.os-version` | all |
| Heading text, main body copy | `rgb(36, 36, 36)` | `h2.large-title.text-center`, `p.body-1.mb-4` | all |
| Body copy, alternate | `rgb(20, 20, 20)` | `p.body-1`, `li.breadcrumb-item a` | all |
| Strongest text: subtitles, card titles under their gradient, announcement label | `rgb(0, 0, 0)` | `p.subtitle-1.heading`, `div.alert-heading` | all |
| Inherited default text | `rgb(50, 49, 48)` | `div.header.header-primary`, `body.refresh.ms-Fabric` | all |
| Header and nav text | `rgb(38, 38, 38)` | `header.uhf-header` | all |
| Muted: list items, breadcrumb current page | `rgb(61, 61, 61)` | `li`, `li.breadcrumb-item` | all |
| Muted: secondary subtitle | `rgb(66, 66, 66)` | `div.subtitle-1.grey-subtitles` | all (`home`) |
| Muted, weakest: footer text, carousel dots | `rgb(97, 97, 97)` | `footer#uhf-footer.uhf-footer.c-uhff`, `button.indicator.current` | all |
| Field border | `rgb(66, 66, 66)` | `select#culture-options` | all |
| Control outline: theme toggle, live-stream pill | `rgb(38, 38, 38)` | `button#dn-theme-toggle.dn-theme-toggle`, `a.uhf-nav-item.uhf-nav-cta` | all |
| Card border hue: purple (supplement) | `rgb(81, 43, 212)` | `a.card.purple-primary` | all |
| Card border hue: magenta (supplement) | `rgb(214, 0, 170)` | `a.card.magenta-primary` | all |
| Card border hue: blue (supplement) | `rgb(11, 108, 255)` | `a.card.blue-primary` | all |
| Card border hue: flamingo (supplement) | `rgb(246, 81, 99)` | `a.card.flamingo-primary` | all (`learn`) |
| Gradient end stop: red (supplement) | `rgb(203, 65, 80)` | `p.subtitle-1.heading.gradients-multi-color-magenta…` | all |
| Focus outline: buttons (supplement) | `rgb(0, 0, 0) solid 1px`, offset `2px` | `a.btn.btn-primary` on focus | all |
| Focus outline: cards and links (supplement) | `currentColor dashed 1px`, offset `1px` | `a.card`, `a.arrow-link` on focus | all |
| Focus outline: nav items (supplement) | `rgb(38, 38, 38) dashed 1px`, offset `-2px`, with an underline | `a.uhf-nav-item` on focus | 1440 |

The site renders no success, danger, or warning status color, and no
data-series colors beyond the gauge art. Those roles are left out.

### Gradients (supplement)

Recorded because they are measured. Every one of them is on `spec.md`'s
do-not-reproduce list as a signature motif.

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Gradient text: numerals, heading phrase, card title | `linear-gradient(128.87deg, rgb(81, 43, 212) 14.05%, rgb(11, 108, 255) 89.3%)`, `background-clip: text` | `p.display-1.gradients-multi-color-purple-blue` | all |
| Gradient text: page title | `linear-gradient(128.87deg, rgb(214, 0, 170) 14.05%, rgb(81, 43, 212) 89.3%)`, `background-clip: text` | `h1.large-title.mb-2.text-fill-transparent` | all (`learn`) |
| Gradient text: card titles, one per hue | purple to magenta, magenta to red, blue to purple, flamingo to purple, at the same angle and stops | `p.subtitle-1.heading.gradients-multi-color-*` | all |
| Call-to-action band fill | `linear-gradient(128.87deg, rgb(11, 108, 255) 14.05%, rgb(81, 43, 212) 89.3%)` | `section.get-started.get-started-blue` | all |
| Page wash, top left | `radial-gradient(… rgba(214, 0, 170, 0.2) 1.43%, rgba(214, 0, 170, 0) 100%)` | `div.radial-gradient.radial-gradient-magenta-tint-2…` | all (`learn`) |
| Logo strip edge fade | `linear-gradient(90deg, rgb(250, 250, 250), rgba(255, 255, 255, 0.2))` | `div.fading-bg.fading-bg-left` | all |

## Type families

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Display: hero, section titles, page title, numerals | `"Space Grotesk", Helvetica, Arial, sans-serif` | `h1.display-2.title`, `h2.large-title.text-center` | all |
| Content: body copy, subtitles, item titles, buttons, links | `"Open Sans", Helvetica, Arial, sans-serif` | `p.hero-subtitle.sub-title`, `a.btn.btn-primary` | all |
| Site chrome and inherited default: header, nav, breadcrumb, announcement body | `"Segoe UI Web (West European)", "Segoe UI", -apple-system, "system-ui", Roboto, "Helvetica Neue", sans-serif` | `div.header.header-primary` | all |
| Footer and site name | `"Segoe UI", SegoeUI, "Helvetica Neue", Helvetica, Arial, sans-serif` | `footer#uhf-footer.uhf-footer.c-uhff`, `a.uhf-site-logo` | all |
| Icon glyphs | `FabricMDL2Icons` | `i.ms-Icon.ms-Icon--GlobalNavButton` | all |

No family carries a Traditional Chinese face. The page is `en-US`.

## Type scale

Each value is size / line-height, weight.

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Hero display heading | `36px / 44px`, 700 | `h1.display-2.title` | 390 |
| Hero display heading | `48px / 54px`, 700 | `h1.display-2.title` | 768 |
| Hero display heading | `68px / 74px`, 700 | `h1.display-2.title` | 1440 |
| Stat numeral (supplement) | `48px / 58px`, 700 | `p.display-1.gradients-multi-color-purple-blue` | 390 |
| Stat numeral (supplement) | `60px / 70px`, 700 | `p.display-1.gradients-multi-color-purple-blue` | 768 |
| Stat numeral (supplement) | `78px / 75px`, 700 | `p.display-1.gradients-multi-color-purple-blue` | 1440 |
| Section title, page title | `28px / 30px`, 700 | `h2.large-title.text-center`, `h1.large-title.mb-2` | 390 |
| Section title, page title | `32px / 44px`, 700 | `h2.large-title.text-center`, `h1.large-title.mb-2` | 768 |
| Section title, page title | `40px / 45px`, 700 | `h2.large-title.text-center`, `h1.large-title.mb-2` | 1440 |
| Subsection title | `26px / 28px`, 600 | `h2.title-1.mb-4` | 390 |
| Subsection title | `28px / 30px`, 600 | `h2.title-1.mb-4` | 768 |
| Subsection title | `32px / 36px`, 600 | `h2.title-1.mb-4` | 1440 |
| Hero subtitle (supplement) | `24px / 36px`, 600 | `p.hero-subtitle.sub-title` | 390 |
| Hero subtitle (supplement) | `28px / 40px`, 600 | `p.hero-subtitle.sub-title` | 1440 |
| Item title: column and resource headings | `20px / 24px`, 600 | `h2.title-3` | 390 |
| Item title | `24px / 26px`, 600 | `h2.title-3`, `h3.title-3.mb-3` | 768 |
| Item title | `24px / 32px`, 600 | `h2.title-3` | 1440 |
| Card title and subtitle (supplement) | `18px / 24px`, 600 | `p.subtitle-1.heading` | 390 |
| Card title and subtitle (supplement) | `20px / 25px`, 600 | `p.subtitle-1.heading` | 768, 1440 |
| Lead line (supplement) | `17px / 25.5px`, 600 | `p.subtitle-2.mb-6` | 390 |
| Lead line (supplement) | `18px / 27px`, 600 | `p.subtitle-2.body` | 1440 |
| Body copy (supplement) | `16px / 18px`, 400 | `p.body-1.mb-4` | 390 |
| Body copy (supplement) | `16px / 22px`, 400 | `p.body-1.mb-4` | 768, 1440 |
| Button label | `16px / 24px`, 600 | `a.btn.btn-primary` | all |
| Small button label (supplement) | `14px / 20px`, 600 | `div.alert-promo a.btn.btn-primary` | all (`learn`) |
| Arrow link (supplement) | `16px / 24px`, 600 | `a.arrow-link` | all |
| Chrome default: header, breadcrumb | `14px / 21px`, 400 | `div.header.header-primary`, `li.breadcrumb-item` | all |
| Nav item | `13px`, 400 | `button.uhf-nav-item.uhf-nav-button` | all |
| Site name in header | `18px / 27px`, 600 | `a.uhf-site-logo` | 1440 |
| Caption (supplement) | `12px / 18px`, 400 | `p.caption-1.os-version.text-center` | all |
| Footer text | `11px / 16.5px`, 400 | `footer#uhf-footer.uhf-footer.c-uhff` | all |

## Spacing scale

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Content side padding | `10px` | `div.content-container` | 390 |
| Content side padding | `20px` | `div.content-container` | 768 |
| Content side padding | `40px` | `div.content-container` | 1440 |
| Content max width | `1400px` | `div.content-container` | all |
| Header max width | `1600px` | `div.uhf-header__container` | 1440 |
| Header side padding | `0px 15px` | `header.uhf-header.uhf-breakpoint--mobile` | 390, 768 |
| Header side padding | `0px 72px` | `header.uhf-header.uhf-breakpoint--desktop` | 1440 |
| Hero top padding | `70px` | `div#mainContent.jumbotron.mx-auto` | all |
| Gap between sections (supplement) | `32px` | `div.content-container` and `section.grid-wrapper.grid-card`, bottom margin | 390, 768 |
| Gap between sections (supplement) | `60px` | `div.content-container` and `section.grid-wrapper.grid-card`, bottom margin | 1440 |
| Grid gap, row and column | `24px 12px` | `section.grid-wrapper.mb-0` | 390 |
| Grid gap | `24px` | `section.grid-wrapper.mb-0` | 768 |
| Grid gap, row and column | `48px 32px` | `section.grid-wrapper.mb-0` | 1440 |
| Topic-card grid gap | `32px 12px` | `section.grid-wrapper.app-types` | 390 |
| Topic-card grid gap | `32px` | `section.grid-wrapper.app-types` | 1440 |
| Card padding | `20px` | `a.card.purple-primary` | all |
| Panel padding (supplement) | `20px 24px` | `section.grid-wrapper.grid-card` | 390 |
| Panel padding (supplement) | `28px 48px` | `section.grid-wrapper.grid-card` | 768 |
| Panel padding | `80px 108px` | `section.grid-wrapper.grid-card` | 1440 |
| Call-to-action band padding (supplement) | `20px 24px` / `28px 48px` / `40px 108px` | `section.get-started.get-started-blue` | 390 / 768 / 1440 |
| Button padding | `12px 20px` | `a.btn.btn-primary` | all |
| Small button padding (supplement) | `6px` | `div.alert-promo a.btn.btn-primary` | all (`learn`) |
| Announcement padding | `6px 24px 6px 44px` | `div.alert-promo.alert` | all (`learn`) |
| Breadcrumb padding | `6px 12px` | `div.breadcrumb-wrapper` | 390 |
| Breadcrumb padding | `6px 40px` | `div.breadcrumb-wrapper` | 1440 |
| Inline gap: wrapped link row | `12px` | `div.flex.flex-wrap` | all |
| Inline gap: header controls | `8px`, `10px` | `button.uhf-contextual-nav-trigger`, `div.uhf-header-l0__actions` | 390 |
| Inline gap: card content stack | `16px` | `div.p-6.gap-3` | 1440 |
| Inline gap: logo strip | `20px` | `div.scroll-wrapper.flex-row` | 1440 |

## Radius

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Large panel: learning panel, gradient band, carousel card | `32px` | `section.grid-wrapper.grid-card`, `section.get-started`, `figure.card-center.card` | all (`figure` at 1440) |
| Card and video | `20px` | `a.card.purple-primary`, `lite-youtube.rounded-lg` | all |
| Small panel: community panel, announcement | `12px` | `section.grid-wrapper.grid-card`, `div.alert-promo.alert` | all |
| Button | `8px` | `a.btn.btn-primary` | all |
| Field | `4px` | `select#culture-options` | all |
| Nav pill call to action | `3px` | `a.uhf-nav-item.uhf-nav-cta` | 1440 |
| Pill: theme toggle | `999px` | `button#dn-theme-toggle.dn-theme-toggle` | all |
| Pill: carousel dot | `9999px` | `button.indicator.current` | all |

## Shadow

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Card at rest | `rgba(0, 0, 0, 0.04) 0px 2px 4px 0px` | `a.card.purple-primary` | all |
| Card on hover (supplement) | `rgba(0, 0, 0, 0.1) 0px 2px 4px 0px` | `a.card` on hover | all |

No other element casts a shadow. Panels and the header are flat.

## Line weights (supplement)

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Card border | `2px solid` | `a.card.purple-primary` | all |
| Button border | `2px solid` | `a.btn.btn-primary`, `a.btn.btn-default` | all |
| Carousel dot border | `2px solid` | `button.indicator` | all |
| Control outline: theme toggle, nav pill | `1px solid` | `button#dn-theme-toggle.dn-theme-toggle`, `a.uhf-nav-item.uhf-nav-cta` | all |
| Field border | `1px solid` | `select#culture-options` | all |

## Breakpoints

The parent-brand stylesheet is cross-origin (`uhf.microsoft.com`), so its
queries are hidden. The site's own sheets declare `min-width` 540, 845,
860, 1084, 1248, 1400, 1467, and 1600px, plus `max-width` 539, 767, 860,
and 1083px. The rows below are the widths where a 4px sweep from 320 to
1600px saw the layout change.

| Role | Value | Element | Viewport |
| --- | --- | --- | --- |
| Grids go from 1 to 2 columns, content padding from 10 to 20px | `min-width: 540px` (declared, observed) | `section.grid-wrapper.app-types`, `div.content-container` | sweep |
| `home` hero and community panel re-grid | `min-width: 845px` (declared, observed between 845 and 848) | `home` hero and stat grids | sweep |
| Header goes from two rows to one row with full nav | `min-width: 860px` (declared, observed) | `header.uhf-header`, from `uhf-breakpoint--mobile` to `--desktop` | sweep |
| Grids go from 2 to 4 columns, content padding from 20 to 40px | `min-width: 1248px` (declared, observed) | `section.grid-wrapper.app-types`, `div.content-container` | sweep |

The other changes the sweep saw are text-driven, not breakpoints: the
workload link row wrapping at 360, 416, 664, 1228, and 1268, and the logo
strip at 496 and 524.
