# LP-0002-02 · Decision

**Question:** on a phone, how heavy should the first-login law picker be?

## Winner: A · full page (`full-page.html`)

Onboarding is its own screen, shown before the dashboard. One card per law
with its 中文 name and article count, a display-name field, a primary
「開始學習」, and a text-style 「略過，顯示全部法規」.

Rationale presented in the review: it is the clearest choice. Its cost is one
extra screen before the first quiz. Variant A means onboarding gets its own
route, so the PRD's route contracts follow from that.

## Rejected

- **B · modal checklist** (`modal-checklist.html`). It is the lightest, but a
  learner can tap 略過 without reading, and the overlay covers the dashboard
  they are about to use.
- **C · dashboard chips** (`dashboard-chips.html`). It never interrupts, but
  it is the most likely to be ignored. On a phone it also pushes 開始新測驗
  further down the first screen.

## What the real implementation must keep

- Its own route, rendered in the normal `base.html` shell with the header in
  place, and no nav link active.
- Order: title, subtitle, display-name field with hint, law list, primary
  button, skip.
- One tappable card per law, built as a native checkbox inside a `<label>`
  with a minimum tap height of 48px. A checked card shows a primary border
  and the `--alert-primary-background` fill. Cards stack in one column on a
  phone and form a 2×2 grid from 768px. The form is capped near 640px wide
  and centered from 768px.
- Article counts come from `get_available_law_types`, as the zh-TW count.
  The list order follows `LAW_TYPES`.
- The skip action stays visible on the first phone screen, under the primary
  button. At 390x844 the whole form fits without scrolling.
- Copy as shown in the mock. It was proposed in the review, and the final
  wording is fixed in the PRD the user approves:
  - Title 「選擇你要準備的法規」. Subtitle 「法規選單只會列出你選的法規，之後可在帳戶設定更改。」
  - Field label 「顯示名稱」. Hint 「不修改就沿用目前名稱」.
  - Law list label 「準備的法規（可複選）」.
  - Buttons 「開始學習」 and 「略過，顯示全部法規」.
- Colors and spacing come from `design-tokens.css`. Muted text reads
  `--neutral-gray-600`, because `style.css`'s `--text-secondary` alias points
  at a token that does not exist.
- The `/account` page reuses this picker (ticket Details). It does not reuse
  the name field, because editing the name after onboarding is out of scope.

Stand-ins in the mock: the name `learner-3fa9c2` and the 專利審查基準 count
(96 條).

## Who decided, on what evidence

Johnny Chang picked A on 2026-10-18, after reviewing all nine shots in
`shots/`. The phone shots were the primary evidence:
`full-page-phone.png`, `modal-checklist-phone.png`, and
`dashboard-chips-phone.png`, each with its tablet and desktop pair.
