---
name: schema-check
description: "Gate every MongoDB schema change: a field added, renamed, removed, or retyped (in a dataclass or in any insert, `$set`, or query); an index added, dropped, or changed in `init_db()`; a new collection; or a `LAW_TYPES` key change. Checks data integrity, plans the migration, and only then writes `docs/modules/db/data-model.md`, the schema's single source of truth. Also use when `tests/test_schema_drift.py` fails."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# Schema Check

[`docs/modules/db/data-model.md`](../../../docs/modules/db/data-model.md) is
the schema's single source of truth. This skill is the only path that writes
it, and it writes **only after every check below passes**. A Change Log row
therefore means the change was confirmed safe.

If a check fails, stop. Report which check failed, what is unsafe, and what
would make it safe. Write nothing to `data-model.md`. Never answer a design
question on the user's behalf. Ask, or leave it on the ticket.

## 1. Is this a schema change?

Yes, if any of these hold:

- A field is added, renamed, removed, or retyped. This covers a dataclass in
  `db/models.py` and any insert, `$set`, `$inc`, `$push`, `$addToSet`,
  `$unset`, `$rename`, or query in `routes/`, `services/`, or `scripts/`.
- An index is added, dropped, or changed in `Database.init_db()`.
- A new collection is read or written.
- A `LAW_TYPES` key is added, renamed, or removed. Keys are stored as data.

Find every write site, not just the one the ticket names. The drift test
cannot catch an ad hoc `$set`, so this grep is the check:

```bash
rg -n 'insert_one|insert_many|update_one|update_many|replace_one|find_one_and_update|bulk_write|\$set|\$inc|\$push|\$addToSet|\$unset|\$rename|create_index|drop_index' routes services scripts db
```

## 2. Integrity checklist

Read `data-model.md` (tables and Change Log) first, then answer each item
with evidence. "Probably fine" is a fail.

- [ ] **Existing documents conform.** Documents already stored still match
      the new shape, or a migration backfills them. A new required field
      always needs a backfill or a reader-side default.
- [ ] **Unique index preflight.** Before adding or tightening a unique index,
      query the target DB for duplicates on the exact key, and for an
      existing index with the same keys under another name (a spec conflict).
      Do this locally, and on production before deploy. Use the snippet below.
- [ ] **Dropped index names are real.** Each `drop_index` name matches an
      actual name in `index_information()` on production, not a guess.
- [ ] **References stay valid.** `law_id`, `question_id`, `user_id`, and
      `base_question_id` still point at live documents of the stored type
      (`user_id` is an `ObjectId`; `law_id` and `question_id` are hex strings).
- [ ] **`init_db()` stays idempotent.** It runs on every boot. A second run
      must be a no-op, and it must not drop and recreate on every start.
- [ ] **No new swallow.** A new `create_index` is not wrapped in
      `try/except: pass`. A blocked unique index must fail startup.

Preflight snippet. It is read-only and gets its DB through the `db.models`
singleton:

```bash
MONGO_URI="<target uri>" python - <<'EOF'
from db.models import db
coll, keys, name = "laws", ["article_number", "lang", "type"], "article_number_lang_type_unique"
c = db.db[coll]
dups = list(c.aggregate([
    {"$group": {"_id": {k: f"${k}" for k in keys}, "n": {"$sum": 1}}},
    {"$match": {"n": {"$gt": 1}}},
], allowDiskUse=True))
same_keys = [n for n, i in c.index_information().items() if [k for k, _ in i["key"]] == keys and n != name]
print(f"{coll}: {len(dups)} duplicate groups {dups[:5]}; same keys under other names: {same_keys}")
EOF
```

For production, use `MONGO_URI="$(heroku config:get MONGO_URI -a <app>)"`.

Known swallows that are still open: four non-unique `i18n_mapping`
`create_index` calls, and the broad `drop_index` excepts in `init_db()`. They
are deliberately left alone pending a production check (LP-0001-01 Deferred
Decisions). Flag them when a change touches those lines. Do not silently
"fix" them.

## 3. Migration

Whenever existing data must change, order the work **expand → migrate →
contract**, and ship each step separately when readers would otherwise break:

1. **Expand:** the code writes the new shape and reads both the old and new
   shapes. Add new indexes now.
2. **Migrate:** backfill or rewrite the existing documents with a script.
3. **Contract:** remove the old reads and the old field, and drop the old
   indexes only after the migration has run everywhere.

Convention:

- One file per change: `scripts/migrations/YYYYMMDD_<slug>.py`. The first
  real migration creates the folder.
- Idempotent. A second run finds nothing to do.
- Dry-run by default: it prints how many documents match. It writes only with
  `--apply`.
- It gets its DB through the `db.models` singleton (`MONGO_URI`), as
  `scripts/migrations/20261016_remove_username_only_users.py` does.
- Run it by hand, locally first and then with
  `heroku run -a <app> python scripts/migrations/<file>.py --apply`. There is
  no runner and no tracking collection.

```python
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from db.models import db  # noqa: E402

FILTER = {"<field>": {"$exists": False}}  # matches only what is still unmigrated

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
col = db.db['<collection>']
print(f"{db.db.name}.<collection>: {col.count_documents(FILTER)} to migrate")
if args.apply:
    result = col.update_many(FILTER, {"$set": {"<field>": "<default>"}})
    print(f"modified {result.modified_count}")
```

## 4. Write (only after 2 and 3 pass)

1. Update the affected `## \`<collection>\`` section in `data-model.md`: the
   `Dataclass:` line, the `### Fields` table (field, type, required,
   references, notes), and the `### Indexes` table. Write index keys exactly
   as `index_information()` returns them, for example
   `[("user_id", 1), ("date", -1)]`. Never list `_id_`. Never put a pipe in a
   cell. Mark a field whose writer is outside this repo `unknown writer`.
   Update the `## LAW_TYPES` table for key changes.
2. Append one Change Log row with the date, the LP id, the change, the
   migration script (or `none`), where it ran, and a link to the
   `docs/changelog/` entry. If the migration or the production preflight has
   not run on Heroku yet, the `Ran` cell reads `pending: heroku`. The owning
   ticket cannot resolve until that cell is filled. Never claim a production
   run that did not happen.
3. Run `pytest tests/test_schema_drift.py`. It must pass. It drops and
   rebuilds its `*_test` database, so it cannot run against production.

## Report

End with:

- Pass or fail for each checklist item, with its evidence.
- The migration plan (expand, migrate, and contract steps), or "none needed".
- What was written to `data-model.md`, or "nothing, because check X failed".
- Anything left `pending: heroku`, and the exact command to clear it.
