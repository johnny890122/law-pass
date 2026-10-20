---
name: neta-design
description: "Build the stage 2 artifact for an `LP-XXXX` ticket: two or three standalone HTML variants that answer one visual question, or design-system directions derived from a `docs/references/` site capture, shot at phone, tablet, and desktop, with the user's pick in `DECISION.md`. Use when a ticket's Details names a visual question, a ticket calls for design-system directions, or the user asks for variants. Not for routine template work, bug fixes, copy changes, or token lookup."
---

# Neta Design

Builds stage 2 of the workflow in `CLAUDE.md`: the variants the user picks
from by looking. The folder contract lives in the `CLAUDE.md` "Artifacts
(conditional)" section. That covers what goes in `artifacts/LP-XXXX-<slug>/`,
how shots are named, what `DECISION.md` records, and the rule that nothing
ships verbatim. This skill is the how-to and does not restate the contract.

**Load the built-in `artifact-design` skill before writing any HTML.** It
covers design fundamentals. This skill covers only what is law_pass-specific
on top of it.

**Invoke `frontend-design:frontend-design` with the Skill tool as the
critic**, at the thesis review and at the self-check. It names the traits
that make a page read as AI-generated. Use it to catch those defaults, not
to pick the look. The ticket's not-open decisions and the token rules win
every conflict: colors come only from tokens, type stays on the contract's
system stacks, and no font is added.

It builds two kinds of artifact. Both follow every step below. They differ
only where a step says so.

| | Ticket variants | Design-system directions |
| --- | --- | --- |
| Question | One screen's visual question, named in its ticket | What the whole app looks like (`LP-0004-05`) |
| Tokens | `static/css/tokens.css`, read-only | One values file per direction in [`tokens/`](tokens/README.md) |
| Source | The current templates and CSS | A `docs/references/<site-slug>/` capture, applied to real screens |

## Trigger Gate

Proceed only when one of these holds:

- The ticket's Details names a visual question, meaning `ticket-system` made
  the artifact call "required".
- The ticket calls for design-system directions.
- The user asks for variants.

Do not trigger for routine template work, bug fixes, copy changes, or a page
that follows an existing template. Those go straight to `templates/`. A
ticket that says `No artifact — <reason>.` gets no artifact. If there is no
ticket yet, write one with `ticket-system` first. When unsure, ask the user
whether they want a variants pass. To look up a token, read
[`tokens/README.md`](tokens/README.md) directly instead.

## Read Order

1. The ticket: the visual question, the variants it names, and the decisions
   it marks as not open.
2. The affected `templates/`, always including `templates/base.html` for the
   shell, plus the rules in `static/css/style.css` that style them.
3. Ticket variants: `static/css/tokens.css`. Directions:
   [`tokens/README.md`](tokens/README.md), [`tokens/_structure.css`](tokens/_structure.css),
   and each `docs/references/<site-slug>/` the ticket names (`spec.md`,
   `tokens.md`, `shots/`).
4. The owning `docs/modules/<module>/index.md` when it exists, for the
   product rules the screen must respect.

A capture is evidence of how another site is built, not a template for
ours. Never reopen the live reference site. If the capture cannot answer a
question, re-capture with `site-capture`.

## Two Tiers

Directions share one system tier and fork only the direction tier.

| Tier | Copies | Contains |
| --- | --- | --- |
| **System** | one, shared | The token contract (`tokens/_structure.css` names), reset and base elements, focus ring, primitives (button, field, card, badge, tab), breakpoints |
| **Direction** | one per direction | Token values (`tokens/<direction>.css`), layout, the nav pattern, how a screen groups its content, `--d-` tokens and direction-only components |

To place something, ask whether the user could point at it and say "that's
why I picked this one". If so, it belongs to the direction. If not, it
belongs to the system. Adding a direction must not need a system-tier edit.
If it does, the boundary is wrong, so fix the boundary rather than
special-casing the direction.

Ticket variants have no tiers. The current app is their system.

## 1. Align

Before the first build, ask one to three questions per round with
AskUserQuestion, and wait for the answers. Confirm three things:

- The visual question, in one sentence.
- The decisions that are not open. Every variant respects them.
- The variants worth building, and what separates them.

If the ticket already settles all three, restate them as one short summary
and ask for a go-ahead instead of asking again. You may assume low-impact
details, but list those assumptions in the review message. If the answers
change the question itself, refine the ticket, not just the artifact.

## 2. Thesis

The bar is **distinct, not tinted**. Variants that differ only in palette
are one variant. Before writing markup, write one sentence per variant that
commits to a layout: what the learner sees first, how the content is
grouped, and how navigation works. If two theses could describe the same
page, start over.

For directions, useful axes are:

| Axis | Range |
| --- | --- |
| Density | Generous whitespace ↔ dense study sheet |
| Navigation | Top nav ↔ bottom tab bar on phone ↔ sidebar on desktop |
| Entry point | Stats first ↔ next quiz first ↔ law browsing first |
| Reading | Law text as UI ↔ law text set apart as a document |
| Tone | Institutional and formal ↔ modern and approachable |

Before sign-off, check each thesis against the generic defaults
`frontend-design` lists. A thesis that lands on one of those defaults
without the ticket asking for it is a default, not a decision. Rewrite it
and tell the user what changed and why.

**Get the theses signed off before building.** A sentence is cheap to change
and a page is not. Each thesis becomes the variant's decision label.

## 3. Ground

The variants show a plausible next version of this app. They are not a new
product.

- Keep the `base.html` shell the same in every ticket variant: logo, nav
  (`首頁` `法條瀏覽` `題庫` `我的進度`), law-type select, `中`/`EN` toggle, and
  user menu. Copy its markup, drop the Jinja, hardcode the active nav link,
  and fill the select with real `name_zh` values from `db/models.py`. A
  direction may restyle and rearrange the shell, since that is its point, but
  it keeps every one of those controls and labels.
- Vary only the thing in question. Everything around it stays identical, so
  the only difference the user sees is the decision.
- Use real labels. Quote Chinese UI copy verbatim from `templates/` and
  `static/js/`. Flag any new copy a variant needs as proposed in the review
  message. Never carry copy from a reference capture.
- Mark stand-in data (questions, scores, counts, user name) with a
  `<!-- stand-in -->` comment on its block, and say so in the review message.
- Law text must be quoted verbatim from `knowledge/` or marked stand-in. Never
  write law text that reads as real when it is not.
- Nothing on a capture's do-not-reproduce list appears in any variant.

## 4. Build

Build one standalone `.html` per variant and name it by its decision, for
example `inline-feedback.html` rather than `variant-b.html`. The file stem is
the `<variant>` in shot names.

A ticket variant mirrors the `<head>` of `base.html`, with paths rewritten
relative to the artifact folder:

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>LP-XXXX · inline feedback</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="../../static/css/tokens.css">
  <link rel="stylesheet" href="../../static/css/style.css">
  <style>/* only what this variant adds */</style>
</head>
```

A direction links nothing from `static/css/`, because mixing two token
systems hides which one a rule reads. It links its values file and the
folder's shared system tier:

```html
<link rel="stylesheet" href="../../.claude/skills/neta-design/tokens/dense-study.css">
<link rel="stylesheet" href="system.css">
<style>/* this direction's layout only */</style>
```

`system.css` holds the system tier: reset, base elements, focus ring, and
primitives, all through contract names. Build **one direction first** and
land it before the next. One direction proves the tier split is real, and
building three at once hides whether it holds.

Variant rules:

- Build two or three variants that differ on the question. Three colorways
  of one layout do not count. When the screen already exists, keep one variant
  close to it as the baseline.
- Label each variant by its decision and state what it trades away. Put the
  label and trade-off in the review message and `DECISION.md`, never in the
  page. The mock must read as product UI, with no notes, captions, or
  "variant A" banners.
- Add no decorative strips, left color bars, rails, gradients, or blobs.
  Reuse the cards, borders, buttons, and spacing already in `style.css`
  before writing new CSS. For a direction, reuse the primitives in
  `system.css`.
- Work mobile-first. Lay out the phone first, then widen with the
  breakpoints `style.css` already uses (`min-width: 768px` and `1024px`).
- Use no JavaScript unless the question is about interaction. If it is, use
  plain inline JS with no framework and no build step.

## 5. Tokens

- Every color, spacing, radius, shadow, and type value is a `var(--…)`. For
  a ticket variant it comes from `static/css/tokens.css`. For a direction it comes from the
  contract or a `--d-` token. Layout geometry is free: widths, grid tracks,
  and breakpoints.
- Never invent a color, a spacing step, or a font size. Never edit
  `static/css/tokens.css` from an artifact.
- If a ticket variant needs a token that does not exist, stop and ask the
  user for it. Do not approximate it with a nearby hex. If a direction needs
  a role the contract lacks, extend the contract as
  [`tokens/README.md`](tokens/README.md) says.
- A direction's values file is written before its HTML. Derive each value
  from the capture's `tokens.md` and comment it with its source, as the
  README shows. Every contract name gets a value.
- Literals live only in token files. Before verifying, this check must print
  nothing:
  `grep -rnE --include='*.html' --include='*.css' '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(' artifacts/LP-XXXX-<slug>/`

## 6. Verify

Serve the repo root so `../../static/` and `../../.claude/` resolve. Run this
in the background and stop it when done:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

For each variant, at **390x844** first, then **768x1024**, then
**1440x900**, use Playwright MCP:

1. `browser_resize`, then `browser_navigate` to
   `http://127.0.0.1:8765/artifacts/LP-XXXX-<slug>/<variant>.html`.
2. `browser_console_messages` must show no errors. A 404 on a stylesheet
   means a wrong relative path, so fix the path. Do not hide the failure.
3. `browser_evaluate` this. `tokens` must be non-empty, `pageScroll` false,
   and `overflowing` empty. Read `--primary-primary` for a ticket variant and
   `--color-accent` for a direction:

   ```js
   () => ({
     tokens: getComputedStyle(document.documentElement).getPropertyValue('--primary-primary').trim(),
     pageScroll: document.documentElement.scrollWidth > innerWidth,
     overflowing: [...document.querySelectorAll('body *')]
       .filter(e => e.clientWidth && e.scrollWidth > e.clientWidth + 1
         && getComputedStyle(e).overflowX === 'visible')
       .map(e => e.tagName + '.' + e.className),
   })
   ```

4. `browser_take_screenshot` with filename
   `artifacts/LP-XXXX-<slug>/shots/<variant>-phone.png`, `-tablet.png` at
   768x1024, or `-desktop.png` at 1440x900. Then read the saved PNG, look at
   it, and fix anything wrong before the user sees it.

## 7. Self-check

With `frontend-design` loaded, review every phone shot, then the tablet and
desktop shots, against its list of AI-generated tells and its typography
and structure rules. Check the HTML as well as the pixels: all-caps
labels, `·`-joined meta strings, `→` appended to buttons, numbered markers
on content that is not a sequence, identical cards with one radius and one
shadow, and hover or entrance motion on everything.

- Fix every tell the ticket did not ask for, inside the token rules. If a
  fix needs a token that does not exist, stop and ask, as the Tokens step
  says.
- A tell that comes from verbatim copy in `templates/`, or from a not-open
  decision, stays. Name it in the review message instead.
- Re-run Verify on whatever changed, so the shots match the HTML.
- Report the result in the review message: each tell found, and whether it
  was fixed or kept and why. "None found" is a valid result, but only after
  reading the shots.

## 8. Review and Decide

- Send the user each variant's decision label, what it trades away, and its
  three shot paths, with phone first. Add your assumptions and any proposed
  copy. Ask a specific question, such as whether the feedback belongs above
  or below the options, rather than "any feedback?".
- Revise in rounds until the user picks. Keep their earlier decisions unless
  they reopen them. Re-shoot after every revision so the shots match the HTML.
- Write `DECISION.md` with the fields `CLAUDE.md` lists. "Who decided" names
  the user. "Evidence" names the shots they looked at. Never record a pick the
  user did not make. A blend is a valid winner, as long as it says which part
  came from which variant. For a direction, name the winning values file.
- Tick the ticket's artifact box and hand off to stage 3. Rebuild the winner
  in `templates/` against real data rather than copying the artifact file, and
  fold the decision into the module doc at doc sync. A winning direction is
  adopted by its own ticket, as `LP-0004-07` moved `role-hues-teal.css` into
  `static/css/tokens.css`.
