# 2026-10-19 — Teal is role-hues' main color

**LP ids:** LP-0004-08

`role-hues`, the `LP-0004-06` palette, was compared with three main colors in
[`artifacts/LP-0004-08-main-color/`](../../artifacts/LP-0004-08-main-color/):
purple as the baseline, the capture's blue, and a teal from outside the
capture. The user picked **teal**. Adoption is `LP-0004-07`, filed from this
decision. The app does not change yet.

| Area | Was | Now |
| --- | --- | --- |
| Main color | Purple `#512bd4`, from the capture. | Teal `#00727a`: hover `#005b62` and tint `#e6f1f2`, derived by the capture's own purple steps. It is the one value from outside the dotnet capture (user, 2026-10-19). |
| Flag tokens | `--d-magenta`, `--d-blue`, and `--d-flamingo` named the hue. | `--d-flag-short`, `--d-flag-law`, and `--d-flag-streak` name the meaning, so a hue can change role without a misnamed token. `LP-0004-06`'s artifact reads the new names. |
| Values files | `role-hues.css`. | Plus `role-hues-blue.css` and `role-hues-teal.css`, each differing from `role-hues.css` only in the accent family and, in `blue`, the 法條 flag. |

Details, including the teal tint that sits close to the success tint, are in
the [`DECISION.md`](../../artifacts/LP-0004-08-main-color/DECISION.md).

## Deliberately not done

- Nothing in `static/css/`, `templates/`, or the Python code changed. That
  is `LP-0004-07`.
- No role-map change besides `blue`'s, where 法條 moves to purple. The
  `teal` winner keeps `LP-0004-06`'s map.
- `blue`'s derived `#0061f5` and the purple baseline stay on file as values
  files. They are rejected, not deleted.
