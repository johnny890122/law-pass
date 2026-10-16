---
name: design-variants
description: "Build the stage 2 artifact for an `LP-XXXX` ticket: two or three standalone HTML variants that answer one visual question, screenshots at phone and desktop, and the user's pick in `DECISION.md`. Use when a ticket's Details names a visual question or the user asks for variants. Not for routine template work, bug fixes, or copy changes."
---

# Design Variants

Builds stage 2 of the workflow in `CLAUDE.md`: the variants the user picks
from by looking. The folder contract lives in the `CLAUDE.md` "Artifacts
(conditional)" section. That covers what goes in `artifacts/LP-XXXX-<slug>/`,
how shots are named, what `DECISION.md` records, and the rule that nothing
ships verbatim. This skill is the how-to and does not restate the contract.

## Trigger Gate

Proceed only when one of these holds:

- The ticket's Details names a visual question, meaning `ticket-system` made
  the artifact call "required".
- The user asks for variants.

Do not trigger for routine template work, bug fixes, copy changes, or a page
that follows an existing template. Those go straight to `templates/`. A
ticket that says `No artifact — <reason>.` gets no artifact. If there is no
ticket yet, write one with `ticket-system` first. When unsure, ask the user
whether they want a variants pass.

## Read Order

1. The ticket: the visual question, the variants it names, and the decisions
   it marks as not open.
2. The affected `templates/`, always including `templates/base.html` for the
   shell, plus the rules in `static/css/style.css` that style them.
3. `static/css/design-tokens.css` and `static/css/design-tokens-dark.css`.
4. The owning `docs/modules/<module>/index.md` when it exists, for the
   product rules the screen must respect.

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

## 2. Ground

The variants show a plausible next version of this app. They are not a new
product.

- Keep the `base.html` shell the same in every variant: logo, nav
  (`首頁` `法條瀏覽` `題庫` `我的進度`), law-type select, `中`/`EN` toggle, and
  user menu. Copy its markup, drop the Jinja, hardcode the active nav link,
  and fill the select with real `name_zh` values from `db/models.py`.
- Vary only the thing in question. Everything around it stays identical, so
  the only difference the user sees is the decision.
- Use real labels. Quote Chinese UI copy verbatim from `templates/` and
  `static/js/`. Flag any new copy a variant needs as proposed in the review
  message.
- Mark stand-in data (questions, scores, counts, user name) with a
  `<!-- stand-in -->` comment on its block, and say so in the review message.
- Law text must be quoted verbatim from `knowledge/` or marked stand-in. Never
  write law text that reads as real when it is not.

## 3. Build

Build one standalone `.html` per variant and name it by its decision, for
example `inline-feedback.html` rather than `variant-b.html`. The file stem is
the `<variant>` in shot names. Mirror the `<head>` of `base.html`, with paths
rewritten relative to the artifact folder:

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LP-XXXX · inline feedback</title>
  <link rel="icon" href="data:,">
  <link href="https://cdn.muicss.com/mui-0.10.3/css/mui.min.css" rel="stylesheet">
  <link rel="stylesheet" href="../../static/css/design-tokens.css">
  <link rel="stylesheet" href="../../static/css/design-tokens-dark.css">
  <link rel="stylesheet" href="../../static/css/style.css">
  <style>/* only what this variant adds */</style>
</head>
```

The dark token file only takes effect under `<html data-theme="dark">`. The
app does not set that today, so keep variants light unless the question is
about dark mode.

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
  before writing new CSS.
- Work mobile-first. Lay out the phone first, then widen with the
  breakpoints `style.css` already uses (`min-width: 768px` and `1024px`).
- Use no JavaScript unless the question is about interaction. If it is, use
  plain inline JS with no framework and no build step.

## 4. Tokens

- Every color, spacing, radius, shadow, and type value is a `var(--…)`. It
  comes from a token file or from a `style.css` alias such as `--primary-color`
  or `--card-bg`. Layout geometry is free: widths, grid tracks, and
  breakpoints.
- Never invent a color, a spacing step, or a font size. Never edit the token
  files, which are generated. Changing them needs its own ticket.
- If a needed token is missing, stop and ask the user for it. Do not
  approximate it with a nearby hex.
- Before verifying, this check must print nothing:
  `grep -nE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(' artifacts/LP-XXXX-<slug>/*.html`

## 5. Verify

Serve the repo root so `../../static/` resolves. Run this in the background
and stop it when done:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

For each variant, at **390x844** first and then **1440x900**, use Playwright
MCP:

1. `browser_resize`, then `browser_navigate` to
   `http://127.0.0.1:8765/artifacts/LP-XXXX-<slug>/<variant>.html`.
2. `browser_console_messages` must show no errors. A 404 on a stylesheet
   means a wrong relative path, so fix the path. Do not hide the failure.
3. `browser_evaluate` this. `tokens` must be non-empty, `pageScroll` false,
   and `overflowing` empty:

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
   `artifacts/LP-XXXX-<slug>/shots/<variant>-phone.png`, or `-desktop.png`
   at 1440x900. Then read the saved PNG, look at it, and fix anything wrong
   before the user sees it.

## 6. Review and Decide

- Send the user each variant's decision label, what it trades away, and its
  two shot paths, with phone first. Add your assumptions and any proposed
  copy. Ask a specific question, such as whether the feedback belongs above
  or below the options, rather than "any feedback?".
- Revise in rounds until the user picks. Keep their earlier decisions unless
  they reopen them. Re-shoot after every revision so the shots match the HTML.
- Write `DECISION.md` with the fields `CLAUDE.md` lists. "Who decided" names
  the user. "Evidence" names the shots they looked at. Never record a pick the
  user did not make. A blend is a valid winner, as long as it says which part
  came from which variant.
- Tick the ticket's artifact box and hand off to stage 3. Rebuild the winner
  in `templates/` against real data rather than copying the artifact file, and
  fold the decision into the module doc at doc sync.
