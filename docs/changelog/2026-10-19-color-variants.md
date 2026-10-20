# 2026-10-19 — Three color variants on the dense-tabbar layout; role-hues wins

**LP ids:** LP-0004-06

Three palettes for the `dense-tabbar` layout are on file in
[`artifacts/LP-0004-06-color-variants/`](../../artifacts/LP-0004-06-color-variants/).
Each one answers "where does the color live", and each has a values file in
[`.claude/skills/neta-design/tokens/`](../../.claude/skills/neta-design/tokens/):

- `purple-line`: the color lives in the lines.
- `role-hues`: the color lives in flags, each hue with one meaning.
- `purple-tint`: the color lives in tinted surfaces.

After the first review, the user asked for the designs to read less
AI-generated. That pass reopened the panel treatment, the metric strip's
form, and the emoji section markers. The user then ruled out any Ming face,
so all text is 黑體. The user picked **`role-hues`**. Before adoption,
`LP-0004-08` compares its main color, purple, with blue and a derived teal.
The app does not change, so no module doc takes the decision yet.

| Area | Was | Now |
| --- | --- | --- |
| Where color lives | `dense-tabbar.css` kept purple to buttons and active states, so the app read gray. | `role-hues`: purple, magenta, blue, and flamingo each keep one meaning on every page, drawn as solid flags. Text stays ink. |
| Role hues | The capture's card hues were unused. | Purple: actions, 選擇題, and 作答題數. Magenta: 簡答題. Blue: 法條. Flamingo: 連續練習天數. All are captured values, held to 3:1 as graphics. |
| 簡答題 badge | Borrowed the warning amber. | Magenta. Status colors only mean status. |
| Containers | Every block was the same rounded white card. | One container per role. The progress numbers and tips are a ruled ledger. The question, the result, and the related list are panels. The law article is a square-cornered sheet. |
| Metric strip | Five big-number tiles. | A ruled ledger. On phone it is five rows, label then number. From 768px it is one row on a five-column grid. |
| Tabs | Pills, for the filter tabs and the active phone tab. | Index tabs on a rule, and a top-edge mark on the active phone tab. |
| Section headings | 💡 學習小提示, 📝 相關題目, 💡 AI 解析（重點）, and 📊 in the law meta line. | No emoji. Proposed copy for `LP-0004-07`. |
| Type | — | 黑體 only (user, 2026-10-19). A Ming law face was tried and dropped. |

The rules adoption must keep are in the
[`DECISION.md`](../../artifacts/LP-0004-06-color-variants/DECISION.md).

## Deliberately not done

- The main color is not final. `LP-0004-08` compares purple, blue, and a
  derived teal before adoption.
- `LP-0004-07` (adoption) is not filed yet. It is filed once `LP-0004-08`
  picks the main color, because adoption takes that palette.
- Nothing in `static/css/`, `templates/`, or the Python code changed.
- No dark mode. No gradient, gradient text, radial wash, or per-card hue
  rotation.
- Emoji on controls (📢, ☆, 💡 查看解析) stay. Only section markers were
  dropped.
