# 2026-10-16 — schema-check skill

**LP ids:** LP-0001-01

The schema now has one source of truth.
[`docs/modules/db/data-model.md`](../modules/db/data-model.md) documents
every collection the code touches, seeded from the real write sites rather
than the dataclasses. The new
[`schema-check`](../../.claude/skills/schema-check/SKILL.md) skill is the only
path that writes it, and only after its integrity checklist passes.
`tests/test_schema_drift.py` fails when code and doc disagree.

| Area | Was | Now |
| --- | --- | --- |
| Schema truth | Split across the dataclasses in `db/models.py`, `init_db()`, and ad hoc writes. `sessions` and `law_types` had no record at all. | `data-model.md` records each collection's writers, fields, indexes, and the `LAW_TYPES` values, with a Change Log. Code must match it. |
| Schema changes | Landed inline, with no checklist or migration. | `schema-check` gates them: integrity checklist, unique-index preflight, expand → migrate → contract, and only then a Change Log row. |
| Migrations | None. | One-off `scripts/migrations/YYYYMMDD_<slug>.py`, dry-run by default and writing only with `--apply`. Run by hand, locally and then via `heroku run`. No runner or tracking collection. |
| Drift detection | None. | `tests/test_schema_drift.py` fails, naming `schema-check`, when the live indexes after `init_db()`, the `LAW_TYPES` keys, or a dataclass field disagree with the doc. |
| `init_db()` unique indexes | `laws.article_number_lang_type_unique` and `user_daily_stats.user_id_date_law_type_unique` were wrapped in `try/except: pass`, so a duplicate key failed silently. | Both raise at startup with pymongo's error, which names the index, like the other five unique indexes. |
| Workflow docs | No schema rule. `docs/modules/index.md` did not exist. | `CLAUDE.md` states that schema changes run `schema-check` and names `data-model.md` as db's module doc. `docs/modules/index.md` is the owner map. |

Deploy note: the baseline Change Log row reads `pending: heroku` until
production is checked for duplicates on both unique keys and for a same-key
index under another name. A duplicate would crash-loop the dyno on boot, so
the check runs before this deploys.

Update 2026-10-17: the check is moot. Production moved to a new, empty
`law_pass` database under LP-0003, where `init_db()` built both indexes at
boot. The baseline row records this.

## Deliberately not done

- Mongo `$jsonSchema` validators.
- A migration runner or tracking collection.
- Cleaning up past changes, such as leftover `is_starred` fields.
- Deleting or completing the unused dataclasses. `QuestionModel` still lacks
  `law_type`, `created_at`, and `paired_question_id` (LP-0001-01 Deferred
  Decisions).
- Making the other `init_db()` swallows loud: four non-unique `i18n_mapping`
  indexes and the broad `drop_index` excepts. They need a production check
  first.
- Catching a field written ad hoc through `$set` in the drift test. The
  skill's grep step covers it instead.
