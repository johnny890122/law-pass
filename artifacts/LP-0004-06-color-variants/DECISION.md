# LP-0004-06 · Decision

**Question:** on the `dense-tabbar` layout, where does the color live?

## Winner: `role-hues`

Values file: `.claude/skills/neta-design/tokens/role-hues.css`, with this
folder's `system.css`, `dense-tabbar-layout.css`, and `role-hues-color.css`.

Its thesis: purple, magenta, blue, and flamingo are each pinned to one
meaning on every screen, so a hue tells the learner what kind of thing they
are looking at. The hues are solid flag marks, like the colored index flags
in a 六法全書, and text stays ink. Panels stay white with light lines.

The main color is not final. `LP-0004-08` compares purple with blue and a
derived teal on this palette. Adoption (`LP-0004-07`) waits for that pick.

## Rejected

- **`purple-line`** (`purple-line.css`): every panel, the law sheet, and the
  quiz options have a 2px purple outline. On the graded quiz, the purple
  outlines of the plain options compete with the green and red answer
  outlines, and the page reads heavier than the other two.
- **`purple-tint`** (`purple-tint.css`): the shell, the ledger band, and the
  start block sit on accent tints. The two stacked tinted blocks drift back
  toward the card look, and the tints are only about 1.1:1 on the ground, so
  the quiz pages barely change.

## What the real implementation must keep

- **The role map.**
  - Purple is the accent: actions, links, the active tab, the progress
    fill, 選擇題, and 作答題數.
  - Magenta is 簡答題, blue is 法條, and flamingo is 連續練習天數.
  - 掌握題數 and 平均得分率 stay neutral.
  - Success, danger, warning, and info stay semantic, and 簡答題 no longer
    borrows the warning amber.
  - The 每日平均得分率 chart color (`--color-data-2`) goes neutral, because
    blue means 法條.
- **Hues are flags, held to 3:1 as graphics.**
  - Badges are solid hue with a white label: magenta is 4.73:1.
  - The ledger and the 選擇題 and 簡答題 tabs carry small flag keys.
  - The law sheet has a blue flag on its top edge.
  - Text stays ink, except the accent's actions and links. The captured
    hues are used as-is, with no derived darker text values.
- **One container per role**, from the less-AI pass the user asked for:
  - A **ledger** with rules only: the five progress numbers and the tips.
    On phone it is a list, with the label on the left and the number on the
    right. From 768px it is one row on a `repeat(5, minmax(max-content, 1fr))`
    grid, with each label and number on a shared baseline.
  - A **panel**: the question, the graded result, and the related-questions
    list.
  - A **sheet**: the law article, with `--radius-sm` corners.
  - The filter tabs are index tabs on a rule. The active phone tab is
    marked on its top edge, not with a filled pill.
- **All text is 黑體** (`--font-body`). The user ruled out any Ming face.
- **Proposed copy for `LP-0004-07`.** 學習小提示, 相關題目, and
  AI 解析（重點） drop their emoji, and so does the 📊 in the law meta line.
  Emoji on controls stay.
- **The shared tiers diverged from `LP-0004-05`'s.** This folder's
  `system.css` has index tabs and a callout without an outline.
  `dense-tabbar-layout.css` has the ledger, the sheet, and the index-tab
  row. The index-tab row draws its rule as an inset shadow, because the
  row scrolls sideways and clips a border. Adoption starts from these
  copies, not from `LP-0004-05`'s.

Stand-ins in the mock are the same as in `LP-0004-05`: the user name, the
five progress numbers, the question and its options, the AI explanation, the
related-question counts, and the attempt count and average. Article 22's text
is verbatim from `knowledge/patent_law_zh.md`.

## Who decided, on what evidence

Johnny Chang picked `role-hues` on 2026-10-19, after reviewing the 36 shots
in `shots/`, phone first. Those are the shots of the less-AI pass, after the
switch to 黑體. Johnny Chang also directed that pass and ruled out the
Ming face. In the same message he asked for main colors other than purple
to be compared, which is `LP-0004-08`.
