# Data Model

The schema's single source of truth. Code must match this file. This file
never follows code silently.

## Rules

- **Change it only through `schema-check`.** Any schema change runs the
  [`schema-check`](../../../.claude/skills/schema-check/SKILL.md) skill. The
  skill writes here only after its integrity checklist passes, so every
  Change Log row is a confirmed change.
- **Write sites, not dataclasses, are the evidence.** A field is documented
  because something writes it. A field whose writer lives outside this repo
  is marked `unknown writer`.
- **Startup is loud.** `init_db()` runs on every boot (`app.py`) and must stay
  idempotent. A unique index that cannot be built raises, which names the
  index, instead of being swallowed.
- **Migrations** follow expand → migrate → contract and live in
  `scripts/migrations/YYYYMMDD_<slug>.py`. They are dry-run by default and
  write only with `--apply`. They are run by hand, locally first and then via
  `heroku run`. There is no runner and no tracking collection.
- **Drift is a test failure.** `tests/test_schema_drift.py` parses this file.
  It fails when the live indexes after `init_db()`, the `LAW_TYPES` keys, or a
  dataclass field disagree with what is written here.

Format the test relies on: each collection has a `` ## `name` `` heading, an
optional `Dataclass:` line, a `### Fields` table, and a `### Indexes` table.
Index keys are written as `index_information()` returns them. The implicit
`_id_` index is not listed. Table cells never contain a pipe.

Conventions used below:

- `ObjectId` means a BSON ObjectId. `hex str` means an ObjectId stored as its
  24-character string.
- `user_id` is written as an `ObjectId` everywhere, although the dataclasses
  annotate it `str`.
- `law_id` and `question_id` are written as `hex str` everywhere.

## `laws`

Law articles, one document per article, language, and law type. Shared
content.

Dataclass: `LawModel`

Writers: `routes/admin.py` (`POST /api/admin/init-laws`, which upserts
`asdict(LawModel)`). Articles for law types other than the mock source are
loaded by scripts outside this repo (`unknown writer`).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `article_number` | str | yes | — | Display label, e.g. 「第 1 條」. Part of the unique key. |
| `content` | str | yes | — | Article text. |
| `chapter` | str | yes | — | Chapter label. |
| `type` | str | yes | `LAW_TYPES` key | Default `patent-act`. |
| `article_number_int` | int | yes | — | Sort key. Default `0`. |
| `lang` | str | yes | — | `zh-TW` or `en`. |

Known issue: `init-laws` upserts on `{"article_number": ...}` alone, which is
narrower than the unique key. An article with the same number in another
law type or language is replaced rather than added. Not yet ticketed.

Legacy: `knowledge/truth_law.json` still carries the single-user fields
`is_starred`, `total_score`, `attempt_count`, and `avg_score`. Old loads may
have stored them on `laws`. No current code reads or writes them there.

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `article_number_int_1` | `[("article_number_int", 1)]` | no |
| `chapter_1` | `[("chapter", 1)]` | no |
| `lang_1` | `[("lang", 1)]` | no |
| `type_1` | `[("type", 1)]` | no |
| `type_1_lang_1` | `[("type", 1), ("lang", 1)]` | no |
| `type_1_article_number_int_1` | `[("type", 1), ("article_number_int", 1)]` | no |
| `article_number_lang_type_unique` | `[("article_number", 1), ("lang", 1), ("type", 1)]` | yes |

## `questions`

Generated questions. Shared content, soft-deleted.

Dataclass: `QuestionModel`. It lacks `law_type`, `created_at`, and
`paired_question_id`, which the scripts write.

Writers: `scripts/generate_questions_remote.py`,
`scripts/generate_examination_questions.py`, and `routes/quiz.py` (soft
delete).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `law_id` | hex str | yes | `laws._id` | |
| `type` | str | yes | — | `MCQ` or `ShortAnswer`. |
| `content` | str | yes | — | Question text. |
| `correct_answer` | str | yes | — | |
| `ai_explanation` | str | yes | — | |
| `lang` | str | yes | — | `zh-TW` or `en`. |
| `options` | list[str] or null | no | — | MCQ only. Null for `ShortAnswer`. |
| `is_deleted` | bool | yes | — | Soft delete. Set `true` by `DELETE /api/quiz/questions/<id>`. |
| `base_question_id` | str (uuid4) | no | other `questions` with the same value | Links a zh-TW/en pair. Written by `services/translator.py` output. |
| `paired_question_id` | hex str | no | `questions._id` | Second pair link, written only by `generate_questions_remote.py` bilingual mode. Not read by the app. |
| `law_type` | ObjectId | no | `law_types._id` | Written only by `generate_examination_questions.py`. Not a `LAW_TYPES` key. Not read by the app. |
| `created_at` | datetime | no | — | Written only by `generate_examination_questions.py`. |
| `is_starred` | bool | no | — | Legacy. No writer since stars moved to `user_question_stars`. May linger on old documents. |

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `law_id_1` | `[("law_id", 1)]` | no |
| `is_deleted_1_type_1` | `[("is_deleted", 1), ("type", 1)]` | no |
| `law_id_1_lang_1` | `[("law_id", 1), ("lang", 1)]` | no |
| `base_question_id_1_lang_1` | `[("base_question_id", 1), ("lang", 1)]` | no |
| `lang_1` | `[("lang", 1)]` | no |

## `i18n_mapping`

Pairs a zh-TW law article with its English counterpart. Read by
`routes/laws.py` to switch languages on the law detail page.

Dataclass: `I18nMappingModel`

Writers: `unknown writer`. Nothing in this repo writes it.

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `zh_tw_law_id` | hex str | yes | `laws._id` | `unknown writer` |
| `en_law_id` | hex str | yes | `laws._id` | `unknown writer` |
| `article_number` | str | yes | — | `unknown writer` |
| `type` | str | yes | `LAW_TYPES` key | `unknown writer` |

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `article_number_idx` | `[("article_number", 1)]` | no |
| `zh_tw_law_id_idx` | `[("zh_tw_law_id", 1)]` | no |
| `en_law_id_idx` | `[("en_law_id", 1)]` | no |
| `type_article_idx` | `[("type", 1), ("article_number", 1)]` | no |

## `users`

Accounts. Each has exactly one identity: a Google-verified `email`
(LP-0002-01) or a LINE user ID in `line_user_id` (LP-0009). A first sign-in
with either provider creates the account (self-signup), the only way an
account is made. There is no linking: one person who uses both providers has
two accounts. Admins view and edit users in Atlas.

Dataclass: `UserModel`

Writers: two inserts, both through `services/auth.py` `_find_or_create`:
`find_or_create_user` on a first Google sign-in and
`find_or_create_line_user` on a first LINE sign-in. `services/auth.py`
`create_session` sets `last_login` on sign-in. Deleted by
`scripts/migrations/20261016_remove_username_only_users.py`, which matches
only users with neither a string `email` nor a string `line_user_id`.

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `username` | str | yes | — | Stored label, not a login credential. Unique. `learner-` plus 6 hex characters, set at signup. |
| `display_name` | str | yes | — | The same random name as `username` at signup, until onboarding (LP-0002-02) changes it. Google and LINE profile data are never stored. |
| `email` | str or null | no | — | Google accounts only: matched against Google's verified email, stored stripped and lowercased. Null on LINE accounts. Unique among strings. |
| `line_user_id` | str or null | no | — | LINE accounts only: the LINE ID token's `sub`, stored as sent (case-sensitive). It belongs to the LINE provider that owns the channel. Null on Google accounts made since LP-0009, and missing on older ones. Unique among strings. |
| `created_at` | datetime | yes | — | UTC. |
| `last_login` | datetime or null | yes | — | Null until first sign-in. |

### Indexes

`email_1` and `line_user_id_1` are partial: they index and enforce
uniqueness only where the field is a string, so null and missing values
never clash. The drift test checks keys and uniqueness, not the filter.
`init_db()` drops a pre-LP-0009 `email_1` that has no filter, once, and
rebuilds it partial.

| Name | Keys | Unique | Partial filter |
| --- | --- | --- | --- |
| `username_1` | `[("username", 1)]` | yes | — |
| `email_1` | `[("email", 1)]` | yes | `{"email": {"$type": "string"}}` |
| `line_user_id_1` | `[("line_user_id", 1)]` | yes | `{"line_user_id": {"$type": "string"}}` |

## `user_progress`

Per-user mastery state for one question.

Dataclass: `UserProgressModel`

Writers: `routes/quiz.py` (answer submit and appeal).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `user_id` | ObjectId | yes | `users._id` | |
| `question_id` | hex str | yes | `questions._id` | |
| `correct_streak` | int | yes | — | Mastered at `>= 3`. |
| `needs_review` | bool | yes | — | `correct_streak < 3`. |
| `last_score` | float | yes | — | `0.0`, `0.5`, or `1.0`. |
| `is_appealed` | bool | yes | — | |

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `user_id_1_question_id_1` | `[("user_id", 1), ("question_id", 1)]` | yes |
| `user_id_1_needs_review_1` | `[("user_id", 1), ("needs_review", 1)]` | no |
| `user_id_1` | `[("user_id", 1)]` | no |

## `user_law_stars`

Per-user starred law articles.

Dataclass: `UserLawStarModel`

Writers: `routes/laws.py` (star toggle, which inserts or deletes).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `user_id` | ObjectId | yes | `users._id` | |
| `law_id` | hex str | yes | `laws._id` | |
| `created_at` | datetime | yes | — | UTC. |

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `user_id_1_law_id_1` | `[("user_id", 1), ("law_id", 1)]` | yes |
| `user_id_1` | `[("user_id", 1)]` | no |

## `user_law_stats`

Per-user running score for one law article.

Dataclass: `UserLawStatsModel`

Writers: `routes/quiz.py` (answer submit and appeal).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `user_id` | ObjectId | yes | `users._id` | |
| `law_id` | hex str | yes | `laws._id` | |
| `total_score` | float | yes | — | |
| `attempt_count` | int | yes | — | |
| `avg_score` | float | yes | — | `total_score / attempt_count`. |

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `user_id_1_law_id_1` | `[("user_id", 1), ("law_id", 1)]` | yes |
| `user_id_1` | `[("user_id", 1)]` | no |

## `user_question_stars`

Per-user starred questions.

Dataclass: `UserQuestionStarModel`

Writers: `routes/laws.py` and `routes/quiz.py` (two star toggles, which
insert or delete).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `user_id` | ObjectId | yes | `users._id` | |
| `question_id` | hex str | yes | `questions._id` | |
| `created_at` | datetime | yes | — | UTC. |

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `user_id_1_question_id_1` | `[("user_id", 1), ("question_id", 1)]` | yes |
| `user_id_1` | `[("user_id", 1)]` | no |

## `user_daily_stats`

Per-user study totals for one UTC day and law type. Feeds the progress page.

Dataclass: `UserDailyStatsModel`

Writers: `services/progress.py` (`upsert_daily_stats`, an upsert on the
unique key).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `user_id` | ObjectId | yes | `users._id` | |
| `date` | str | yes | — | `YYYY-MM-DD`, UTC. |
| `law_type` | str | yes | `LAW_TYPES` key | |
| `questions_answered` | int | yes | — | `$inc` per answer. |
| `total_score` | float | yes | — | `$inc` per answer. |
| `laws_covered` | list[hex str] | yes | `laws._id` | `$addToSet`. |
| `mastered_count` | int | yes | — | Snapshot of mastered questions for this law type at the last update. |

### Indexes

| Name | Keys | Unique |
| --- | --- | --- |
| `user_id_date_law_type_unique` | `[("user_id", 1), ("date", 1), ("law_type", 1)]` | yes |
| `user_id_law_type_date_desc` | `[("user_id", 1), ("law_type", 1), ("date", -1)]` | no |

## `sessions`

One quiz session and its answers.

No dataclass.

Writers: `routes/quiz.py` (create, `$push` an answer, `$set` on appeal).

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `user_id` | ObjectId | yes | `users._id` | |
| `type` | str | yes | — | `MCQ`, `ShortAnswer`, or `Mixed`. |
| `mode` | str | yes | — | `new`, `review`, or `mixed`. |
| `law_type` | str | yes | `LAW_TYPES` key | |
| `question_ids` | list[hex str] | yes | `questions._id` | |
| `answers` | list[object] | yes | — | Starts empty. One entry per submit. |
| `answers[].question_id` | hex str | yes | `questions._id` | |
| `answers[].user_answer` | str | yes | — | |
| `answers[].score` | float | yes | — | Flipped by an appeal. |
| `answers[].feedback` | str | yes | — | An appeal prefixes it with 「[已申訴]」 and a space. |
| `answers[].is_appealed` | bool | yes | — | |
| `answers[].submitted_at` | datetime | yes | — | UTC. |
| `created_at` | datetime | yes | — | UTC. |
| `status` | str | yes | — | Only `active` is ever written. |

### Indexes

None beyond `_id_`.

## `law_types`

Law-type records used by one question-generation script. Not the same as
`LAW_TYPES` below.

No dataclass.

Writers: `unknown writer` (`scripts/init_law_types_remote.py`, which is not
in this repo). Reader: `scripts/generate_examination_questions.py`.

### Fields

| Field | Type | Required | References | Notes |
| --- | --- | --- | --- | --- |
| `slug` | str | yes | — | The script looks up `examination`. Other fields are `unknown writer`. |

### Indexes

None beyond `_id_`.

## LAW_TYPES

`LAW_TYPES` in `db/models.py` is the law-type registry. Its keys are stored
as data in `laws.type`, `i18n_mapping.type`, `sessions.law_type`, and
`user_daily_stats.law_type`. Renaming or removing a key is a schema change
that needs a migration.

| Key | name_zh | name_en |
| --- | --- | --- |
| `patent-act` | 專利法 | Patent Law |
| `patent-examination` | 專利審查基準 | Patent Examination Guidelines |
| `administrative-appeal` | 訴願法 | Administrative Appeal Act |
| `administrative-litigation` | 行政訴訟法 | Administrative Litigation Act |

## Code

- `db/models.py`: `LAW_TYPES`, the dataclasses, and `Database.init_db()`.
- `app.py`: calls `init_db()` on every startup.
- `tests/test_schema_drift.py`: enforces this file.
- `.claude/skills/schema-check/SKILL.md`: the only path that writes here.

## Change Log

A row means `schema-check` confirmed the change. `Ran` reads
`pending: heroku` until a migration or production check has run on Heroku,
and the owning ticket cannot resolve until that cell is filled.

| Date | LP | Change | Migration | Ran | Changelog |
| --- | --- | --- | --- | --- | --- |
| 2026-10-16 | LP-0001-01 | Baseline seeded from write sites. `init_db()` now raises when `laws.article_number_lang_type_unique` or `user_daily_stats.user_id_date_law_type_unique` cannot be built. | none | local: fresh DB passes. heroku: the duplicate and same-key-name query never ran, and is moot. Production moved to a new, empty `law_pass` database (LP-0003), where `init_db()` built both indexes at boot on release v4 and `GET /health` returned 200 on 2026-10-17. | [2026-10-16-schema-check](../../changelog/2026-10-16-schema-check.md) |
| 2026-10-16 | LP-0002-01 | `users.email` added (str, required, lowercased) with unique index `email_1`; `username` becomes a stored label. `find_or_create_user` inserts users on a first Google sign-in (self-signup), and `scripts/add_user.py` is deleted. Username-only users and their documents in the six per-user collections are deleted, not backfilled. | `scripts/migrations/20261016_remove_username_only_users.py` | local: `patent_act` has 0 users, so the migration and the `email` preflight are no-ops; fresh DB builds `email_1`. pending: heroku, owned by LP-0007. Neither the production migration (`--apply`) nor the `email` duplicate preflight has run. | [2026-10-16-google-sign-in](../../changelog/2026-10-16-google-sign-in.md) |
| 2026-10-18 | LP-0009 | `users.line_user_id` added (str or null) with unique partial index `line_user_id_1`. `users.email` becomes optional (null on LINE accounts), and `email_1` becomes unique partial over strings: `init_db()` drops the unfiltered `email_1` once and rebuilds it. A second insert writer, `find_or_create_line_user`, shares `_find_or_create` with Google. The LP-0002-01 cleanup is narrowed to users with neither identity, so it never deletes LINE accounts. | none (`init_db()` rebuilds `email_1`); `scripts/migrations/20261016_remove_username_only_users.py` edited | local: `law_pass` holds the unfiltered `email_1` and 0 users, `lp_report_0002_01` 1 user with a string email; no duplicate string emails and no `line_user_id` anywhere. `tests/test_migrations.py` shows the rebuild and that a second `init_db()` is a no-op. Booting the app on `law_pass` rebuilt `email_1` partial and built `line_user_id_1`, and a real LINE signup then wrote one doc with `email: None` (2026-10-18). pending: heroku. The production preflight (distinct string emails, and `email_1` the real name of the unfiltered index) and the boot-time rebuild have not run. | [2026-10-18-line-login](../../changelog/2026-10-18-line-login.md) |
