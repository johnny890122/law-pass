#!/usr/bin/env python3
"""LP-0002-01: delete users with neither an email nor a LINE ID, and every per-user document keyed on them.

Dry-run by default (prints counts); deletes only with --apply. Idempotent.

Usage:
  MONGO_URI=<target uri> python scripts/migrations/20261016_remove_username_only_users.py
  MONGO_URI=<target uri> python scripts/migrations/20261016_remove_username_only_users.py --apply
"""

import argparse
import os
import sys

# LP-0009: LINE accounts have email None, so match on neither identity being a string.
FILTER = {
    'email': {'$not': {'$type': 'string'}},
    'line_user_id': {'$not': {'$type': 'string'}},
}
PER_USER = ['user_progress', 'user_law_stars', 'user_law_stats', 'user_question_stars', 'user_daily_stats', 'sessions']


def migrate(database, apply: bool) -> dict:
    """Return per-collection counts: what matches on a dry run, what was deleted on apply."""
    ids = [user['_id'] for user in database.users.find(FILTER, {'_id': 1})]
    counts = {}
    # Per-user documents first and users last, so a crash midway leaves the user for a rerun to find.
    for name in PER_USER:
        query = {'user_id': {'$in': ids}}
        counts[name] = database[name].delete_many(query).deleted_count if apply else database[name].count_documents(query)
    counts['users'] = database.users.delete_many({'_id': {'$in': ids}}).deleted_count if apply else len(ids)
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete username-only users and their per-user documents.')
    parser.add_argument('--apply', action='store_true', help='delete; without it, only print counts')
    args = parser.parse_args()

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from db.models import db  # importing builds no indexes, so this is safe before deploy

    counts = migrate(db.db, args.apply)
    verb = 'deleted' if args.apply else 'to delete (dry run; pass --apply)'
    for name, count in counts.items():
        print(f"{db.db.name}.{name}: {count} {verb}")
