---
id: LP-0004-01
title: Site-capture skill for external reference sites
type: story
status: resolved
priority: medium
created: 2026-10-17
resolved: 2026-10-17
area: docs
parent: LP-0004
tags:
  - skills
  - design-system
---

# Site-capture skill for external reference sites

## Description

`neta-design` derives the design system's tokens from a reference site, so
it needs a durable written record of that site that no one has to reopen
the live site to use. A `site-capture` skill, ported from neta-homepage's
`site-capture` and its `MR-0007-01` reference-spec template, produces it.

## Details

- Current: no capture skill and no record of any reference site.
- Desired: `.claude/skills/site-capture/SKILL.md`, ported from
  `/Users/johnnychang/moblab/neta-homepage/.claude/skills/site-capture/`
  and the spec template in that repo's
  `docs/issues/resolved/MR-0007-reference-site-adaptation/MR-0007-01-reference-spec-extraction.md`:
  - **Trigger:** the user names a reference site to learn from, or a
    ticket calls for a capture. Never for capturing law_pass itself.
  - **Confirm first:** the URL and the scope (homepage only, or named
    pages) with the user.
  - **Output** in `docs/references/<site-slug>/`, every file dated:
    - `spec.md`: identification (URL, date read, kind of site, and why it
      suits a law-exam quiz app), screen and section order named by
      **function**, navigation model, layout at 390x844 / 768x1024 /
      1440x900 (what reflows, collapses, or hides), a component inventory,
      each interaction classed `static ok` / `needs JS` / `needs server`,
      and a **do-not-reproduce** list (logos, mascots, illustrations,
      signature motifs, copy).
    - `tokens.md`: measured values for color roles, type families and
      scale, spacing scale, radius, shadow, and breakpoints. Each value
      names the element and viewport it was read from.
  - **Measurement:** Playwright MCP `browser_evaluate` on computed styles
    at the three viewports, not eyeballed from screenshots.
  - **Screenshots:** every captured page at the three viewports, committed
    to `docs/references/<site-slug>/shots/<page>-phone.png`, `-tablet.png`,
    and `-desktop.png`, so later sessions and the user can look at them.
  - **Rules:** descriptive only. Re-capture, never patch. Download or
    commit no asset from the site: screenshots are the only image kept.
    Carry no headline or body copy from the reference.
  - **Output check:** `neta-design` can derive a token file and a layout
    from `docs/references/<site-slug>/` without opening the live site.
- Dropped from the neta reference: the full crawl, `sitemap.md`,
  `inventory.md`, and `findings.md` of an owned site (we capture
  references, not our app); verbatim copy preservation (reversed here: no
  copy at all); never committing screenshots (reversed here: they are
  committed); Wix specifics; the 1555x885 and 375x812 viewports.
- `CLAUDE.md`: add `docs/references/` to the doc tree and name the skill.
- No artifact — this story builds a tool and has no screen choice.
- No PRD — tooling.
- Out of scope: capturing a real reference (`LP-0004-04`) and deriving the
  token contract (`LP-0004-02`).

## Acceptance Criteria

- [x] `.claude/skills/site-capture/SKILL.md` covers the trigger,
      confirmation, output files, measurement method, rules, and output
      check above.
- [x] `CLAUDE.md` lists `docs/references/` in the doc tree and names the
      skill.
- [x] `pytest` green: no code or test change. The box stays to confirm
      nothing regressed. 71 passed.
- [x] `flake8` clean.
- [x] Seen working: a smoke capture of one public site's homepage, made by
      following the skill, yields `spec.md`, `tokens.md`, and its three
      `shots/`, with every token traceable to an element and viewport. The
      smoke output is deleted, not committed. law.moj.gov.tw, driven through
      a local Playwright script running the skill's own measure snippet,
      because another session held the Playwright MCP browser. The smoke
      added page scroll and container `max-width` to the script.
- [x] Docs synced: `CLAUDE.md` and a changelog entry. No module doc
      applies, because no product behavior changes.

## Open Questions

- None.

## Related Files

- `.claude/skills/site-capture/SKILL.md`
- `CLAUDE.md`
- `docs/references/`

## Handoff Appendix

### Settled Decisions

- Reference screenshots are committed to `docs/references/<site-slug>/shots/`
  so later sessions and the user can look at them. Neta's never-commit rule
  is reversed. Decided by the user on 2026-10-17.

## Resolution

Landed the `site-capture` skill, which writes `spec.md`, `tokens.md`, and
committed `shots/` for an external reference into `docs/references/`, and
listed that folder in `CLAUDE.md`. No real reference was captured
(`LP-0004-04`). See
[2026-10-17-site-capture-and-neta-design](../../../changelog/2026-10-17-site-capture-and-neta-design.md).
