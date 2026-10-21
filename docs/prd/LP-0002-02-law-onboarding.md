---
ticket: LP-0002-02
status: draft
created: 2026-10-18
approved:
reviewer:
---

# PRD: First-login onboarding to set your name and pick the laws you study

Implements `LP-0002-02`, filed as `LP-0002-02-law-onboarding.md` and listed
in [docs/issues/](../issues/README.md). Its folder follows its status.
Behavior, scope, and settled decisions live in the ticket and are not
restated here. The screen is variant A from
[artifacts/LP-0002-02-law-onboarding/DECISION.md](../../artifacts/LP-0002-02-law-onboarding/DECISION.md).

Implementation choices the user confirmed at the gap analysis
(2026-10-18):

- The study set is read from the DB on each request and cached in `flask.g`.
  It is not copied into the session.
- Only the dashboard (`/`) gates on onboarding. The sign-in callbacks are
  unchanged.
- `/account` is reached through an account icon in the user menu at every
  width. From 1024px the display name also links to it.
- "First chosen law" means first in `LAW_TYPES` order, and
  `study_law_types` is always stored in that order.

## Before → After

### Study set lookup (new helper)

- **Before:** None (new). Nothing is stored per user.
- **After:**
  1. `services/auth.py` gains `get_study_law_types() -> List[str]`. It
     reads `users.study_law_types` for `session['user_id']` with one
     `find_one` by `_id` and caches the result on `flask.g` for the rest of
     the request. A missing field, a missing user, or no session all return
     `[]`.
  2. It also gains `allowed_law_types() -> List[str]`, which returns the
     study set, or every `LAW_TYPES` key when the set is empty (BR-1).

### Current law type

- **Before** (`services/auth.py:169-193`): `get_current_law_type` returns
  `session['current_law_type']`, or `patent-act` when the key is missing.
  `set_current_law_type` accepts any `LAW_TYPES` key.
- **After:**
  1. `get_current_law_type` reads the session value. If the value is
     missing or not in `allowed_law_types()`, it writes
     `allowed_law_types()[0]` to the session and returns it (BR-3). Login
     clears the session, so each login starts on the first chosen law. A
     settings change takes effect on the next request.
  2. `set_current_law_type` returns `False` for a key outside
     `allowed_law_types()`.
  3. Every existing caller keeps its signature: `routes/quiz.py`,
     `routes/laws.py`, `routes/frontend.py:101`, `routes/law_types.py`, and
     `services/inventory.py`.

### Header switcher

- **Before** (`routes/law_types.py:21-56`, `:93-146`;
  `static/js/main.js:148-187`): `GET /api/law-types` lists all four types.
  `POST /api/law-types/select` accepts any `LAW_TYPES` key.
- **After:**
  1. `GET /api/law-types` lists only the entries whose `type` is in
     `allowed_law_types()`, in `LAW_TYPES` order. `current` comes from
     `get_current_law_type()`.
  2. `POST /api/law-types/select` returns 400 for a key outside the allowed
     set. The message is in the contract below.
  3. `main.js` is unchanged. It already builds the options from the
     response.

### Sign-in landing

- **Before** (`routes/auth.py:47-68`, `:82-102`; `routes/frontend.py:13`):
  the callbacks redirect to the validated `next`, or to `/`. `/` renders
  `dashboard.html`.
- **After:**
  1. The callbacks are unchanged.
  2. `GET /` reads the user's `onboarded_at`, using the same `flask.g`
     lookup as the study set. If it is missing, `/` returns 302 to
     `/onboarding`. Otherwise it renders `dashboard.html` as before (BR-4).
     A missing user document counts as onboarded and renders the dashboard
     (BR-9).

### Onboarding

- **Before:** None (new).
- **After:**
  1. `GET /onboarding` renders `onboarding.html` with the current
     `display_name` and the four laws from `get_available_law_types()`, all
     unticked. An onboarded learner who opens it gets a 302 to `/` (BR-5).
  2. The form posts to `POST /onboarding`, with `action=save` from
     「開始學習」 or `action=skip` from 「略過，顯示全部法規」.
  3. On save, the server validates the name and laws (BR-6, BR-7). It then
     `$set`s `study_law_types` (in `LAW_TYPES` order), `onboarded_at`, and
     `display_name` when the name changed. It updates
     `session['display_name']`, pops `session['current_law_type']`, and
     returns 302 to `/`. The next request lands on the first chosen law
     (BR-3).
  4. On skip, the server `$set`s `onboarded_at` and `study_law_types: []`.
     The name is left unchanged, even if the field was edited (BR-8). It
     pops `session['current_law_type']` and returns 302 to `/`.

### Account settings

- **Before:** None (new). There is no account page.
- **After:**
  1. The header user menu shows an account icon link to `/account` at every
     width. From 1024px, the display name is also a link to `/account`.
  2. `GET /account` renders `account.html`, which holds the same law picker
     as onboarding with the learner's current set ticked. It has no name
     field.
  3. `POST /account` `$set`s `study_law_types` and redirects back to
     `/account` with a 「已儲存」 flash. Saving with nothing ticked stores
     `[]`, meaning all laws. `onboarded_at` is never touched here.

## Route Contracts

### `GET /onboarding`

- **Auth:** `@login_required`.
- **Request:** none.
- **Response:**
  - 200 with `onboarding.html`, given `display_name` and `law_types`, the
    list from `get_available_law_types()`.
  - A learner whose user already has `onboarded_at` gets a 302 to `/`.
- **Errors:** no session → 302 to `/auth/login?next=…`, the existing guard.

### `POST /onboarding`

- **Auth:** `@login_required`. `SESSION_COOKIE_SAMESITE='Lax'` (app.py:38)
  keeps the cookie off cross-site form posts.
- **Request** (form):
  - `action` (str): `save` or `skip`.
  - `display_name` (str, optional): read only on `save`.
  - `law` (str, repeated, zero or more): `LAW_TYPES` keys, read only on
    `save`.
- **Response:** 302 to `/`, after the writes in Before → After §
  Onboarding.
- **Errors:**
  - `action` missing or not `save`/`skip` → 400.
  - A `law` value that is not a `LAW_TYPES` key → 400. Only a tampered form
    can send one.
  - A trimmed `display_name` over 30 characters → 400, re-rendering
    `onboarding.html` with the learner's input and ticks kept, and the error
    「顯示名稱最多 30 個字」 under the field. Nothing is written.
  - Already onboarded → 302 to `/` with nothing written, so a double submit
    is harmless.

### `GET /account`

- **Auth:** `@login_required`.
- **Request:** none.
- **Response:** 200 with `account.html`, given `law_types` and `selected`,
  the stored `study_law_types`.
- **Errors:** no session → 302 to login, the existing guard.

### `POST /account`

- **Auth:** `@login_required`.
- **Request** (form): `law` (str, repeated, zero or more): `LAW_TYPES` keys.
- **Response:** 302 to `/account`, with the flash 「已儲存」.
- **Errors:** a `law` value that is not a `LAW_TYPES` key → 400, with
  nothing written.

### `GET /api/law-types` (changed)

- **Auth:** `@login_required`, unchanged.
- **Response:** 200 with the existing shape
  `{"law_types": [...], "current": "<key>"}`. `law_types` holds only the
  allowed set, in `LAW_TYPES` order.
- **Errors:** unchanged. A failure returns 500 with
  「無法獲取法律類型列表」.

### `POST /api/law-types/select` (changed)

- **Auth:** `@login_required`, unchanged.
- **Request:** JSON `{"law_type": "<key>"}`, unchanged.
- **Response:** 200 with the existing shape.
- **Errors:**
  - Missing `law_type` → 400 「缺少 law_type 參數」, unchanged.
  - A key not in `LAW_TYPES` → 400, the existing 「無效的法律類型: …」 body,
    unchanged.
  - A valid key outside the learner's set → 400
    `{"error": "此法規不在你的學習清單中: <key>", "valid_types": [<allowed keys>]}`
    (proposed copy).

### Unchanged on purpose

The `law_type` read from the query string at `routes/quiz.py:75` and
`routes/laws.py:80`, `:353`, and `:811`, and from the JSON body at
`routes/quiz.py:142`, still accepts any `LAW_TYPES` key. The frontend sends
neither. This follows the ticket's settled decision that the study set is a
UX filter, not access control.

## Data Changes

Each change goes through `schema-check` at implementation. Nothing here is
final until that skill writes `docs/modules/db/data-model.md`.

| Collection | Change | Existing documents | Migration |
| --- | --- | --- | --- |
| `users` | Add `study_law_types`: list of `LAW_TYPES` keys, stored in `LAW_TYPES` order, optional. Written by `POST /onboarding` and `POST /account`. | Conform. A missing field reads as `[]`, meaning all laws. | None |
| `users` | Add `onboarded_at`: datetime (UTC), optional. Written once by `POST /onboarding`. | Conform. A missing field means not onboarded, so every existing learner onboards on their next visit to `/`. | None |
| `users` | `display_name` gains a second writer: `POST /onboarding`, 1–30 characters after trimming. | Conform. | None |

`UserModel` gains `study_law_types: List[str] = field(default_factory=list)`
and `onboarded_at: Optional[datetime] = None`. New signups therefore store
`study_law_types: []` and `onboarded_at: None`, and both read the same as a
missing field. The `display_name` comment "Console-set only." is replaced
with "Set at signup, changeable in onboarding." No index is added, because
both fields are read by `_id`.

## Templates and UI Copy

- `templates/_law_picker.html` (new): the picker partial. One `<label>` card
  per law, with a native checkbox `name="law"`, the `name_zh`, and
  「{count_zh_tw} 條」. It takes `law_types` and `selected`. Onboarding and
  `/account` both include it.
- `templates/onboarding.html` (new): rebuilt from `full-page.html` in the
  artifact against real data. Nothing in the header nav is active. The
  styles the DECISION lists move into `style.css` as classes, using tokens
  only.
- `templates/account.html` (new): a title, the picker, and a 「儲存」
  button. It renders flashed messages.
- `templates/base.html`: `.user-menu` gains an account icon link
  `<a href="/account" id="account-link" class="btn-logout" title="帳戶設定">`
  with a person icon, placed before the logout button and shown at every
  width. `#user-display-name` is wrapped in `<a href="/account">`, which is
  still hidden below 1024px per the UI module.
- Header fit: the UI module says the one-row header at 768px has about 25px
  to spare, and the icon adds about 44px. Step 6 tightens the `.nav` link
  spacing in the 768–1023px range so the row still fits, with no wrapping or
  clipping. If it cannot fit without dropping a control, the work stops and
  the layout goes back to the user. The PRD does not choose one.
- Copy (all proposed, from the artifact):
  - `onboarding.html`:
    - Title 「選擇你要準備的法規」.
    - Subtitle 「法規選單只會列出你選的法規，之後可在帳戶設定更改。」
    - Name label 「顯示名稱」, hint 「不修改就沿用目前名稱」, and error
      「顯示名稱最多 30 個字」.
    - Law list label 「準備的法規（可複選）」.
    - Buttons 「開始學習」 and 「略過，顯示全部法規」.
  - `account.html`:
    - Page title 「帳戶設定」. Section 「準備的法規（可複選）」.
    - Hint 「全部不選即顯示全部法規」.
    - Button 「儲存」. Flash 「已儲存」.
  - Header: account link title 「帳戶設定」.
  - `<title>` blocks: 「設定學習法規 - 專利法 AI 刷題助手」 and
    「帳戶設定 - 專利法 AI 刷題助手」, following the existing
    `{page} - 專利法 AI 刷題助手` pattern.
  - `select` error `此法規不在你的學習清單中: <key>`.

## LLM Prompts

None. The story makes no LLM call.

## Business Rules and Edge Cases

| ID | Rule or scenario | Expected behavior |
| --- | --- | --- |
| BR-1 | An empty or missing `study_law_types` | Means all four laws in every reader: the switcher, `select`, and the default and reset of `current_law_type`. |
| BR-2 | Storage order | `study_law_types` is always written in `LAW_TYPES` order, however the form sends it. |
| BR-3 | `current_law_type` outside the allowed set, or missing | On the next `get_current_law_type()` call, it is reset to `allowed_law_types()[0]` and saved in the session. With an empty set, that is `patent-act`. |
| BR-4 | The onboarding gate | Only `GET /` redirects to `/onboarding`. A sign-in with `?next=/laws` lands on `/laws`, and the learner onboards on their next visit to `/`. |
| BR-5 | `GET` or `POST /onboarding` after onboarding | 302 to `/`, with nothing written. |
| BR-6 | Name on save | Trimmed. Blank or unchanged keeps the current `display_name`, with no write. 1–30 characters is saved to `users.display_name` and `session['display_name']`. Over 30 returns 400 and re-renders. Names need not be unique. |
| BR-7 | Save with no laws ticked | Same as skip, apart from the name: `study_law_types: []`, `onboarded_at` set, and the name saved if it was changed. |
| BR-8 | Skip | Writes `onboarded_at` and `study_law_types: []`. Ignores the name field and the ticks. |
| BR-9 | Session alive, user document deleted in Atlas | The study set reads `[]` (all laws), and `/` treats the learner as onboarded, so no redirect loop. Signing in again creates a new account, as today. |
| BR-10 | A second device holding an older `current_law_type` | Reset on its next request, because the set is read from the DB (BR-3). |
| BR-11 | Language toggle | Unchanged: shown only while `current_law_type` is `patent-act`. |

## Test Plan

No external calls. Tests sign in by writing `user_id`, `username`, and
`display_name` with `client.session_transaction()` against a user inserted
in the test DB, the same as `tests/test_auth.py`.

- `tests/test_onboarding.py`
  - A user with no `onboarded_at` → `GET /` → 302 to `/onboarding`.
  - An onboarded user → `GET /` → 200 dashboard. `GET /onboarding` → 302
    to `/`.
  - `GET /onboarding` → 200, with all four `name_zh` and the current name
    in the input.
  - Save the name `Alice` with `law=administrative-appeal` →
    `users.display_name == 'Alice'`, `session['display_name'] == 'Alice'`,
    `study_law_types == ['administrative-appeal']`, and `onboarded_at` set.
    `GET /auth/current` returns `Alice`.
  - Save a blank name → `display_name` is unchanged.
  - Save a 31-character name → 400, the error copy in the body, and nothing
    written.
  - Save `law=administrative-litigation&law=administrative-appeal` →
    stored as `['administrative-appeal', 'administrative-litigation']`
    (BR-2).
  - Save `['administrative-appeal']` → `GET /api/law-types` returns only
    that law, and `current == 'administrative-appeal'`.
  - `POST /api/law-types/select` with `patent-act` while it is not in the
    set → 400. Then `administrative-appeal` → 200.
  - Skip → `onboarded_at` set, `study_law_types == []`, all four laws
    returned, and `GET /` → 200.
  - Save with no laws ticked → `study_law_types == []` and onboarded
    (BR-7).
  - `POST /onboarding` with `law=trademark-act` → 400, nothing written.
    Missing `action` → 400.
  - Logout and sign in again (a fresh session for the same user) →
    `GET /api/law-types/current` returns the first chosen law, and the set
    is unchanged.
  - The session holds `patent-act`, and `/account` saves
    `['administrative-litigation']` → the next `GET /api/law-types` has
    `current == 'administrative-litigation'` (BR-3).
  - `GET /account` → 200, with the stored laws ticked. `POST /account` with
    none ticked → `study_law_types == []`, and all four laws show.
  - `POST /account` with an unknown key → 400, nothing written.
  - Unauthenticated `GET /onboarding` and `GET /account` → 302 to login.
- `tests/test_schema_drift.py`: unchanged. It goes green once
  `schema-check` has written `data-model.md`.

## Rollout and Migration

- No new env vars or config.
- No migration. Both fields read correctly when missing.
- On deploy, every existing learner, including the account used in
  production checks, lands on `/onboarding` on their next visit to `/`.
- Rollback: revert the commit. Stored `study_law_types` and `onboarded_at`
  values are ignored by older code, so no data needs restoring.

## Implementation Order

1. Run `schema-check` for the two `users` fields. Update `UserModel` and
   `data-model.md` together, so `tests/test_schema_drift.py` stays green.
2. Services: `get_study_law_types`, `allowed_law_types`, and the new
   `get_current_law_type` / `set_current_law_type`, plus their unit tests in
   `tests/test_onboarding.py`.
3. The `GET /api/law-types` filter and the `select` 400, with tests.
4. The `_law_picker.html` partial, `GET/POST /onboarding`, and the
   dashboard gate, with tests.
5. `GET/POST /account` and the header account link in `base.html`, with
   tests.
6. Styles in `style.css`. Check at 390x844, 768x1024, and 1440x900 against
   `docs/modules/ui/index.md`.
7. Docs: `docs/modules/laws/index.md` (new), `docs/modules/index.md`, the
   UI module's header rows (the account icon), and a changelog entry.
