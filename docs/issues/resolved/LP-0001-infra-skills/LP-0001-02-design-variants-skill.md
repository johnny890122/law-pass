---
id: LP-0001-02
title: Design-variants skill for stage 2 artifacts
type: story
status: resolved
priority: medium
created: 2026-10-16
resolved: 2026-10-16
area: ui
parent: LP-0001
tags:
  - skills
  - artifacts
---

# Design-variants skill for stage 2 artifacts

## Description

`CLAUDE.md` says what an artifact folder must contain but not how to build
good variants. A `design-variants` skill, ported lean from moblab's
`claude-design`, covers that how-to so every artifact-backed ticket gets
comparable, token-true variants.

## Details

- Current: the "Artifacts (conditional)" section of `CLAUDE.md` holds the
  folder contract, and `ticket-system` makes the artifact call. No skill
  covers alignment, grounding, variant rules, or verification, and
  `artifacts/` does not exist yet.
- Desired: `.claude/skills/design-variants/SKILL.md`, ported from
  `/Users/johnnychang/moblab/mr_local_prototype/.claude/skills/claude-design/`:
  - **Trigger gate:** a ticket's Details names a visual question, or the user
    asks for variants. It does not trigger for routine template work, bug
    fixes, or copy changes.
  - **Read order:** the ticket, then the affected `templates/` and
    `static/css/style.css`, then the token files.
  - **Alignment:** ask one to three questions per round before the first
    build. Confirm the visual question and which decisions are not open.
  - **Grounding:** keep the `base.html` shell (header, nav, law-type select)
    steady and vary only the thing in question. Use real labels and quote
    Chinese UI copy verbatim. Label stand-in data clearly.
  - **Variant rules:** two or three variants that differ on the question,
    each labeled by its decision with the trade-off stated. Keep design notes
    out of the mock, and add no decorative strips, rails, or gradients.
  - **Tokens:** link `../../static/css/design-tokens.css` and
    `design-tokens-dark.css`. Never invent colors, spacing, or type. If a
    needed token is missing, ask the user for it.
  - **Verification:** use Playwright MCP at phone 390x844 (primary) and
    desktop 1440x900. The console must be clean with no text overflow, and
    the shots go into `shots/<variant>-<viewport>.png`.
  - **Decision:** record it in `DECISION.md` per `CLAUDE.md`, including who
    decided and on what evidence. The winner is rebuilt in `templates/`.
- Folder contract stays exactly as `CLAUDE.md` defines it. The skill points
  to that contract and does not restate it. Trim the `CLAUDE.md` Artifacts
  section to the contract plus a pointer to the skill.
- Dropped from the reference:
  - The React/Babel, deck, animation, tweaks, and device-frame assets.
  - `artifact-brief.md`, `component-selection.md`, and the `final/` package.
  - The `mr-design` dependency, Codex in-app Browser, and Figma.
- No artifact. This story builds the tool that makes artifacts and has no
  screen choice of its own.
- Out of scope: editing the token files, a design-system skill, and building
  an artifact for any real ticket.

## Acceptance Criteria

- [x] `.claude/skills/design-variants/SKILL.md` covers the trigger gate, read
      order, alignment, grounding, variant rules, tokens, verification, and
      decision steps above. It has no Figma, React, or `final/` references.
- [x] The `CLAUDE.md` Artifacts section keeps the contract and points to the
      skill for the how-to. The `ticket-system` Artifact Call section names
      the skill as stage 2's builder.
- [x] `pytest` green: no code or test change. The box stays to confirm
      nothing regressed. 24 passed.
- [x] `flake8` clean. No Python changed here. The 7 pre-existing errors in
      `services/inventory.py`, `services/progress.py`, and
      `tests/test_progress_service.py` were fixed in a separate lint change.
- [x] Seen working: one smoke variant built by following the skill opens in
      Playwright at both viewports with tokens applied and a clean console.
      The smoke output is deleted, not committed.
- [x] Docs synced: `CLAUDE.md` and a changelog entry. No module doc applies,
      because no product behavior changes.

## Open Questions

- None.

## Related Files

- `/Users/johnnychang/moblab/mr_local_prototype/.claude/skills/claude-design/`
  (reference, external)
- `.claude/skills/design-variants/SKILL.md` (new)
- `.claude/skills/ticket-system/SKILL.md`
- `CLAUDE.md`
- `static/css/design-tokens.css`
- `static/css/design-tokens-dark.css`
- `static/css/style.css`
- `templates/base.html`

## Handoff Appendix

### Settled Decisions

- Lean port that fits `CLAUDE.md`'s existing artifact contract. The user
  chose this on 2026-10-16.
- No Figma. The user supplies the design tokens through
  `static/css/design-tokens*.css`. Those files say they are generated from
  Figma, but the skill treats them as the source and never calls Figma
  tools.
- Skill name is `design-variants`. The user called it the "frontend variant
  build skill".

## Resolution

Landed the `design-variants` skill. The `CLAUDE.md` Artifacts section now holds
only the contract plus a pointer, and `ticket-system` names the skill as stage
2's builder. Deliberately not ported: React/Babel, decks, the `final/` package,
and Figma. Full story in
[2026-10-16-design-variants-skill](../../../changelog/2026-10-16-design-variants-skill.md).
