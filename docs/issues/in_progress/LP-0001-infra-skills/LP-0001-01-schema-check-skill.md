---
id: LP-0001-01
title: Schema-check skill with data-model.md as the source of truth
type: story
status: in_progress
priority: medium
created: 2026-10-16
resolved:
area: db
parent: LP-0001
tags:
  - skills
  - schema
  - migrations
---

# Schema-check skill with data-model.md as the source of truth

## Description

The schema has no single source of truth. It is split across dataclasses,
`init_db()`, and ad hoc writes, and changes land with no migration or
integrity check. This story makes `docs/modules/db/data-model.md` the one
truth, and adds a `schema-check` skill that writes to it only after
confirming a change is safe. Every schema change is then checked and logged.

## Details

- Current: the "schema" is split across places that disagree.
  - Dataclasses in `db/models.py`. Only `LawModel` and `UserModel` are ever
    instantiated. `QuestionModel` lacks the `law_type` and `created_at`
    fields that `scripts/generate_examination_questions.py` writes.
  - Collections with no dataclass at all: `sessions` (`routes/quiz.py:33`)
    and `law_types` (read in `scripts/generate_examination_questions.py:43`).
  - Indexes in `Database.init_db()`, run on every startup (`app.py:35`).
    Earlier changes were made inline, such as
    `drop_index('question_id_1')` and `is_starred` (removed by comment only).
    Unique-index creation is wrapped in `try/except: pass`, so a blocked
    constraint fails silently.
  - `LAW_TYPES` keys are stored as data (`type` and `law_type` fields).
  - There are no migrations.
- **Single source of truth:** `docs/modules/db/data-model.md`. Code must
  match it, and it never follows code silently. For each collection it
  records:
  - its purpose and its dataclass, if one exists;
  - a fields table (field, type, required, references, notes);
  - an indexes table (name, keys, unique).

  It also records the `LAW_TYPES` values and a `## Change Log`. It replaces
  the planned `docs/modules/db/index.md`.
- **Gate:** `schema-check` writes to `data-model.md` only after its checklist
  passes. If a check fails, it stops, reports what is unsafe, and writes
  nothing. A row in the Change Log therefore means the change was
  confirmed. The checklist:
  - **What counts as a schema change:**
    - adding, renaming, removing, or retyping a field, whether in a
      dataclass or in an insert, `$set`, or query in `routes/`,
      `services/`, or `scripts/`;
    - adding, dropping, or changing an index in `init_db()`;
    - a new collection;
    - a change to a `LAW_TYPES` key.
  - **Integrity:**
    - existing documents still conform, or a migration backfills them;
    - before adding a unique index, the target DB has been queried and
      contains no duplicates;
    - dropped index names match real index names;
    - references (`law_id`, `question_id`, `user_id`, `base_question_id`)
      stay valid;
    - `init_db()` stays idempotent.
  - **Migration:** whenever existing data must change, use the convention
    below, ordered expand → migrate → contract.
  - **Write:** update the affected tables in `data-model.md` and append a
    Change Log row.
- **Loud `init_db()`:** delete the `try/except: pass` around the two wrapped
  unique-index creations, `laws.article_number_lang_type_unique` and
  `user_daily_stats.user_id_date_law_type_unique`. A duplicate key or a
  spec conflict then raises at startup with pymongo's own message, which
  names the index. The other five unique indexes already behave this way.
  `create_index` with an identical spec is a no-op, so the old reason
  ("index might already exist") never needed a swallow.
  - Deploy risk: a raise crash-loops the Heroku dyno. Before deploying,
    check production for duplicates on both keys, and for a same-key index
    under another name. Record the result in the baseline Change Log row.
- Change Log row: date, LP id, the change, the migration script (or "none"),
  where it ran, and a link to the `docs/changelog/` entry. If a migration
  has not yet run on Heroku, the "ran" cell reads `pending: heroku`, and the
  owning ticket cannot resolve until it is filled.
- Drift test: `tests/test_schema_drift.py` parses `data-model.md` and fails,
  naming `schema-check`, when any of these hold:
  - after `init_db()`, `index_information()` (tests already run against a
    real `patent_act_test`) differs from a collection's index table;
  - the `LAW_TYPES` keys differ from the documented values;
  - a dataclass field is missing from its collection's fields table.

  There is no separate snapshot file. Known ceiling: a field written ad hoc
  through `$set` is not mechanically caught, so the skill's checklist covers
  it with a grep.
- Seeding: build the first `data-model.md` from the real write sites (`rg`
  for inserts and updates), not from the dataclasses. Mark any field whose
  writer is outside this repo (for example, the `law_types` contents) as
  `unknown writer`. The first Change Log row is the baseline, `LP-0001-01`.
- Migration convention: `scripts/migrations/YYYYMMDD_<slug>.py`.
  - Idempotent, dry-run by default (prints match counts), and writes only
    with `--apply`.
  - Run by hand, locally and then via `heroku run`.
  - No tracking collection and no runner.
  - The folder is created by the first real migration.
- No artifact. This story adds a skill, a doc, and a test, and no screen is
  involved.
- Out of scope:
  - Mongo `$jsonSchema` validators.
  - A migration runner or tracking collection.
  - Cleaning up past changes, such as leftover `is_starred` fields.
  - Deleting or completing the unused dataclasses (see Deferred Decisions).

## Acceptance Criteria

- [x] `docs/modules/db/data-model.md` documents every collection the code
      touches, including `sessions` and `law_types`, with fields, indexes,
      `LAW_TYPES`, and a Change Log whose first row is the baseline.
- [x] `.claude/skills/schema-check/SKILL.md` covers the trigger description,
      what counts as a schema change, the integrity checklist, the migration
      convention, expand → migrate → contract ordering, and the
      write-only-after-pass rule.
- [x] The drift test passes on the current tree. A temporary index change
      and a temporary dataclass field each make it fail with a message
      naming `schema-check`. Both edits are then reverted. Verified on
      2026-10-16 in a scratch copy of the tree: a throwaway `laws` index on
      `content` and a throwaway `UserModel` field each failed one test
      naming `schema-check`. The working tree was never edited.
- [x] `init_db()` raises when either of the two formerly wrapped unique
      indexes cannot be created. A test inserts duplicates into a test
      collection with the index dropped, calls `init_db()`, and expects the
      error.
- [ ] Production was checked for duplicates and same-key name conflicts
      before deploy, and the result is in the baseline Change Log row.
- [x] `CLAUDE.md` Workflow states that a schema change runs `schema-check`
      and that `data-model.md` is the schema's source of truth.
- [x] `pytest` green: covered by `tests/test_schema_drift.py` and
      `tests/test_app.py` (the loud `init_db()` case). 27 passed.
- [x] `flake8` clean. The 7 pre-existing errors in `services/inventory.py`,
      `services/progress.py`, and `tests/test_progress_service.py` were fixed in a separate lint change.
- [x] Seen working: `python app.py` still starts with indexes initialized,
      and the drift test catches the throwaway edits described above.
      `python app.py` against the local `patent_act` DB booted, `GET
      /health` returned 200, and both unique indexes exist. No browser
      step: the change has no screen.
- [x] Docs synced: `docs/modules/db/data-model.md` is created and the db row
      in `docs/modules/index.md` points to it. The `CLAUDE.md` Docs tree
      notes that db's module doc is `data-model.md`, and a changelog entry is
      written.

## Open Questions

- None.

## Related Files

- `db/models.py`
- `app.py`
- `routes/quiz.py`
- `routes/laws.py`
- `routes/admin.py`
- `services/auth.py`
- `services/progress.py`
- `scripts/add_user.py`
- `scripts/generate_examination_questions.py`
- `scripts/generate_questions_remote.py`
- `tests/test_app.py`
- `docs/modules/db/data-model.md` (new)
- `docs/modules/index.md` (new)
- `.claude/skills/schema-check/SKILL.md` (new)
- `tests/test_schema_drift.py` (new)
- `CLAUDE.md`

## Handoff Appendix

### Settled Decisions

- `docs/modules/db/data-model.md` is the single source of truth and replaces
  the planned `db/index.md`. The user chose this on 2026-10-16.
- The skill writes to `data-model.md` only after confirming the change is
  safe, so every change is logged. The log is a `## Change Log` table in
  `data-model.md`. The user chose this on 2026-10-16.
- Trigger: the skill description plus a `CLAUDE.md` rule, enforced by the
  drift test because `pytest` is already in the done gate. A PostToolUse
  hook was rejected because it only sees Claude's own edits, not
  hand-written ones.
- Migrations are one-off scripts with no tracking collection. The user
  chose this on 2026-10-16.
- `init_db()` fails loudly when a unique index cannot be created, and that
  fix ships in this story rather than a follow-up. The user chose this on
  2026-10-16.

### Behavior Details

- Doc format the test parses: one `## <collection>` heading per collection,
  with a `### Fields` table and a `### Indexes` table. Index keys are written
  as they appear in `index_information()` (for example,
  `[("user_id", 1), ("question_id", 1)]`). The `_id_` index is implicit and
  not listed.
- Migration scripts get their DB through the `db.models` singleton
  (`MONGO_URI`), the same way `scripts/add_user.py` does.

### Test Scenarios

- `tests/test_schema_drift.py`: the current tree matches `data-model.md`.
- The failure output names the collection, and the index or field, that
  drifted, along with `schema-check`.

### Deferred Decisions

- Whether to delete the unused dataclasses or complete them. With
  `data-model.md` as the truth, they are a second and staler copy. This
  needs a follow-up ticket, not this story.
- The other swallows in `init_db()` stay as they are: four non-unique
  `create_index` calls on `i18n_mapping`, and the broad `drop_index`
  excepts. A same-key index under another name likely explains why they
  were wrapped, so making them loud needs a production check first. The
  skill flags them, and a follow-up ticket decides.
