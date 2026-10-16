# 2026-10-16 — design-variants skill

**LP ids:** LP-0001-02

Stage 2 of the workflow now has a builder. The new
[`design-variants`](../../.claude/skills/design-variants/SKILL.md) skill is a
lean port of moblab's `claude-design`. It turns a ticket's visual question
into two or three token-true HTML variants, verifies them in Playwright, and
records the user's pick. No product behavior changed, so no module doc
applies.

| Area | Was | Now |
| --- | --- | --- |
| Building variants | `CLAUDE.md` set the folder contract, and the how-to was left to whoever built them. | The skill covers the trigger gate, read order, alignment rounds, grounding in the `base.html` shell, variant rules, tokens, verification, and recording the decision. |
| `CLAUDE.md` Artifacts | The contract and some how-to bullets were mixed together. | The section holds the contract only, plus a pointer to the skill. The "differ on the question" and stand-in/token rules moved into the skill. |
| `ticket-system` Artifact Call | Made the call and named no builder. | Names `design-variants` as stage 2's builder. |
| Token use | "Link `design-tokens.css`." | Variants link both token files and `style.css`, and use only `var(--…)` for color, spacing, radius, shadow, and type. A grep check catches raw hex or `rgb()`. If a token is missing, the skill stops and asks the user. |
| Verification | "Screenshot at phone and desktop." | The repo root is served with `http.server` so `../../static/` resolves. Each viewport is checked for a clean console and for the token load, page scroll, and element overflow, and only then screenshotted. The `<head>` skeleton carries `<link rel="icon" href="data:,">` so the browser's automatic `/favicon.ico` request does not leave a 404 in the console. |
| `.gitignore` | `.playwright-mcp/` was untracked clutter after every browser run. | `.playwright-mcp/` is ignored. |

Smoke run: one variant built by following the skill (the quiz config shell
and its radio cards) passed every check at 390x844 and 1440x900 and was then
deleted.

## Deliberately not done

- No React/Babel, deck, animation, tweaks panel, or device frames. The
  variants are static HTML.
- No `artifact-brief.md`, `component-selection.md`, or `final/` package.
  `DECISION.md` is the only record, and the winner is rebuilt in
  `templates/`.
- No `mr-design` dependency, Codex in-app Browser, or Figma. The token files
  are the source.
- The token files were not edited, and no design-system skill was added.
- No artifact was built for any real ticket.
