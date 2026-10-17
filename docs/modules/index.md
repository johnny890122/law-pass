# Modules

Owner map: each area, its module doc, and what it owns. A module doc is
created the first time a ticket changes that area, and gets a row here in the
same change.

| Module | Doc | Owns |
| --- | --- | --- |
| auth | [auth/index.md](auth/index.md) | Who may sign in and how: Google OIDC with self-signup keyed by `users.email`, the login page, logout, sessions, and `login_required`. |
| deploy | [deploy/index.md](deploy/index.md) | CI on GitHub Actions, the `law-pass` Heroku app, auto-deploy of `main`, and the config var inventory. |
| db | [db/data-model.md](db/data-model.md) | MongoDB collections, fields, indexes, `LAW_TYPES`, `init_db()`, and migrations. The schema's single source of truth, written only through the `schema-check` skill. |
