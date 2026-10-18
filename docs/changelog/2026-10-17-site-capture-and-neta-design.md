# 2026-10-17 — site-capture and neta-design skills

**LP ids:** LP-0004-01, LP-0004-02

The design-system workflow from neta-homepage now has its two tools. The new
[`site-capture`](../../.claude/skills/site-capture/SKILL.md) skill turns an
external reference site into a written, measured record in
`docs/references/<site-slug>/`. The new
[`neta-design`](../../.claude/skills/neta-design/SKILL.md) skill replaces
`design-variants`. It keeps every `design-variants` step, adds a token
contract and design-system directions derived from a capture, and shoots at
three viewports. No product behavior changed, so no module doc applies.

| Area | Was | Now |
| --- | --- | --- |
| Reference sites | No way to record one. | `site-capture` confirms the URL and scope, measures computed styles with Playwright at 390x844, 768x1024, and 1440x900, and writes `spec.md` (section order by function, navigation, layout per viewport, components, interactions, do-not-reproduce list) and `tokens.md` (every value tied to an element and a viewport). It never captures law_pass, and it carries no copy and no asset. |
| Reference screenshots | — | Committed to `docs/references/<site-slug>/shots/<page>-{phone,tablet,desktop}.png`. Neta's never-commit rule was reversed by the user. |
| Stage 2 builder | `design-variants`. | `neta-design`. `.claude/skills/design-variants/` is deleted. |
| Token source | Figma-generated `static/css/design-tokens*.css` only. | Ticket variants still use them, read-only. Design-system directions use a values file per direction in `.claude/skills/neta-design/tokens/`, derived from a capture's `tokens.md`, with every value commented as captured or derived. |
| Token contract | None. | `tokens/_structure.css` names the semantic roles `templates/` renders today, including form fields, status colors, disabled states, law text, and the two progress charts, all with placeholder values. `tokens/README.md` holds the admission rule (rendered today and shared by a second direction) and the `--d-` namespace for direction-only tokens. |
| Distinctness | "Three colorways of one layout do not count." | Each variant also gets a one-sentence layout thesis, signed off before building. Directions split into a shared system tier and a forked direction tier. |
| Viewports | Phone 390x844 and desktop 1440x900. | Phone, tablet 768x1024, and desktop, in `neta-design`, the `CLAUDE.md` Artifacts contract, the `ticket-system` artifact box, and `LP-0002-02`'s artifact box. |
| Hex grep | Artifact `*.html`. | Artifact `*.html` and `*.css`, so the shared `system.css` is held to it too. |
| `CLAUDE.md` | No reference captures. | The doc tree lists `docs/references/`, and the Docs and Artifacts sections name both skills. |

Smoke runs, both deleted afterwards:

- `site-capture` on the homepage of law.moj.gov.tw yielded `spec.md`,
  `tokens.md`, and three shots, with every token traced to an element and
  viewport. It exposed two gaps in the measure script, which now reports
  horizontal page scroll and container `max-width`. The capture also found
  the site scrolls sideways at 768x1024.
- `neta-design` derived a values file from that capture alone, then built one
  direction (the dashboard under a shared `system.css`). It passed the hex
  grep, contract coverage, and the Verify step at all three viewports: tokens
  applied, no page scroll, no overflow, and a clean console.

Both smokes drove Playwright through a local script that runs each skill's
own snippet. The Playwright MCP browser was held by another session.

## Deliberately not done

- No real reference was captured. That is `LP-0004-04`, waiting on the
  reference URLs.
- No direction was built and no real token values were set. That is
  `LP-0004-05`.
- `static/css/` is untouched. Adoption is `LP-0004-06`.
- No `demo/` prototype, `/a/` `/b/` `/c/` routes, static export,
  `docs/artifacts/`, `final/`, `artifact-brief.md`, or
  `component-selection.md` came over from neta-homepage.
- No full crawl, `sitemap.md`, `inventory.md`, or `findings.md` came over
  from neta's `site-capture`. Those record an owned site, and we capture
  references.
- The done gate's viewports were not changed. That is `LP-0004-03`.
- Older changelog entries and `LP-0001` tickets keep the `design-variants`
  name and links as history.
