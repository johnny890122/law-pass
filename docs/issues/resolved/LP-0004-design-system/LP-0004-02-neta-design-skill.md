---
id: LP-0004-02
title: Neta-design skill, merged from design-variants
type: story
status: resolved
priority: medium
created: 2026-10-17
resolved: 2026-10-17
area: ui
parent: LP-0004
tags:
  - skills
  - design-system
  - artifacts
---

# Neta-design skill, merged from design-variants

## Description

The design system needs one skill that turns a site capture into tokens and
builds the artifacts the user picks from. `neta-design` starts from our
`design-variants` content, merges in neta-homepage's `neta-design`
additions, and replaces `design-variants`.

## Details

- Current: `design-variants` builds per-ticket variants against
  Figma-generated tokens it may not edit, verifies at phone and desktop
  only, and has no token contract and no path from a reference to tokens.
- Desired: `.claude/skills/neta-design/`.
  - **Kept from `design-variants`:** trigger gate, read order, align,
    ground (the `base.html` shell, verbatim zh-TW copy, `<!-- stand-in -->`
    markers, the law-text rule), build and variant rules, the verify
    script, review, and `DECISION.md`. The folder contract stays in the
    `CLAUDE.md` Artifacts section.
  - **Merged in from
    `/Users/johnnychang/moblab/neta-homepage/.claude/skills/neta-design/`:**
    - Load the built-in `artifact-design` skill before writing HTML.
    - Token contract: `tokens/README.md` holds the admission rule (a role
      earns a place only when a law_pass screen renders it and a second
      direction would name it) and the `--d-` namespace for direction-only
      tokens. `tokens/_structure.css` holds semantic role names with
      placeholder values, scoped to what `templates/` renders today.
    - One values file per direction, derived from a
      `docs/references/<site-slug>/tokens.md`, with each value commented
      with its source.
    - "Distinct, not tinted": directions differ in layout, not only palette.
      Each gets a one-sentence thesis, signed off before building.
    - Two tiers: system (contract, base, primitives, breakpoints) and
      direction (values, layout).
  - **Token rule change:** a design-system artifact links its direction's
    values file from `tokens/`. `static/css/design-tokens*.css` stays
    untouched until `LP-0004-06`. The hex grep still applies to artifact
    HTML, so literals live only in token files.
  - **Viewports:** verify and shoot at 390x844, 768x1024, and 1440x900, into
    `shots/<variant>-phone.png`, `-tablet.png`, and `-desktop.png`.
  - **Dropped from neta:** the `demo/` Starlette prototype, `/a/` `/b/`
    `/c/` routes, static export, the `docs/artifacts/` location, `final/`,
    `artifact-brief.md`, `component-selection.md`, and NETA content.
    `DECISION.md` already records what the implementation must keep.
- Removal and repointing:
  - Delete `.claude/skills/design-variants/`.
  - `CLAUDE.md` Artifacts section: point to `neta-design` and add tablet.
  - `ticket-system` `SKILL.md`: the Artifact Call names `neta-design`, and
    its acceptance box text adds tablet (768x1024).
  - `prd-report` `SKILL.md`: repoint its reference to the `design-variants`
    Verify step.
  - Refine pending `LP-0002-02`: its artifact box adds tablet.
  - Changelog entries and `LP-0001` tickets keep the old name as history.
- No artifact — this story builds a tool and has no screen choice.
- No PRD — tooling.
- Out of scope: real token values (they need `LP-0004-04`), building
  directions (`LP-0004-05`), and editing `static/css/` (`LP-0004-06`).

## Acceptance Criteria

- [x] `.claude/skills/neta-design/SKILL.md` keeps every `design-variants`
      step listed above and adds the merged sections. It has no `demo/`,
      export, `final/`, or NETA references.
- [x] `tokens/README.md` and `tokens/_structure.css` exist. The contract
      names cover what `templates/` renders, with placeholder values marked.
- [x] `.claude/skills/design-variants/` is deleted. `rg design-variants`
      hits only changelog entries and `LP-0001` tickets. Rewritten: it also
      hits the `LP-0004` epic and this ticket, which describe the
      replacement, and the generated `done.md` and `in-progress.md`, which
      list those tickets' titles.
- [x] The `CLAUDE.md` Artifacts section, `ticket-system`, `prd-report`, and
      `LP-0002-02` name `neta-design` and the three viewports. Rewritten:
      `CLAUDE.md` and `ticket-system` name both. `prd-report` names
      `neta-design`, and its report viewports are its own rule, unchanged.
      `LP-0002-02` names the three viewports, and it never named a builder.
- [x] `pytest` green: no code or test change. The box stays to confirm
      nothing regressed. 71 passed.
- [x] `flake8` clean.
- [x] Seen working: one smoke variant, built by following the skill, opens
      in Playwright at all three viewports with tokens applied, no page
      scroll, and a clean console. The smoke output is deleted, not
      committed. A direction built from the `LP-0004-01` smoke capture,
      checked with the skill's own Verify snippet through a local Playwright
      script, because another session held the Playwright MCP browser.
- [x] Docs synced: `CLAUDE.md` and a changelog entry. No module doc
      applies, because no product behavior changes.

## Open Questions

- None.

## Related Files

- `.claude/skills/neta-design/`
- `.claude/skills/design-variants/SKILL.md`
- `.claude/skills/ticket-system/SKILL.md`
- `.claude/skills/prd-report/SKILL.md`
- `CLAUDE.md`
- `docs/issues/pending/LP-0002-invite-only-beta/LP-0002-02-law-onboarding.md`

## Resolution

Landed `neta-design` in place of `design-variants`, with a token contract
scoped to `templates/`, capture-derived direction values, and three-viewport
verification. No direction was built and `static/css/` is untouched
(`LP-0004-05`, `LP-0004-06`). See
[2026-10-17-site-capture-and-neta-design](../../../changelog/2026-10-17-site-capture-and-neta-design.md).
