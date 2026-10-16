"""Schema drift: docs/modules/db/data-model.md is the schema's source of truth (LP-0001-01).

A failure means code and the doc disagree. Fix it by running the schema-check
skill, never by silently editing the doc to match the code.
"""
import ast
import dataclasses
import os
import re
from pathlib import Path

import pytest

DOC = Path(__file__).resolve().parent.parent / "docs" / "modules" / "db" / "data-model.md"


def _report(problems):
    return (
        "Schema drift against docs/modules/db/data-model.md:\n  - " + "\n  - ".join(problems)
        + "\nRun the schema-check skill (.claude/skills/schema-check/SKILL.md) before changing the schema or the doc."
    )


def _rows(chunk):
    """Body rows of the one Markdown table in chunk, as cells with backticks stripped."""
    lines = [line.strip() for line in chunk.splitlines() if line.strip().startswith("|")]
    return [[cell.strip().strip("`") for cell in line.strip("|").split("|")] for line in lines[2:]]


def _subsection(body, heading):
    return next((part for part in re.split(r"^### ", body, flags=re.M) if part.startswith(heading)), "")


def parse_doc(text):
    """Return ({collection: {dataclass, fields, indexes}}, {LAW_TYPES keys})."""
    sections = {chunk.split("\n", 1)[0].strip(): chunk for chunk in re.split(r"^## ", text, flags=re.M)[1:]}
    collections = {}
    for heading, body in sections.items():
        name = re.fullmatch(r"`(\w+)`", heading)
        if not name:
            continue
        dataclass = re.search(r"^Dataclass: `(\w+)`", body, flags=re.M)
        collections[name.group(1)] = {
            "dataclass": dataclass.group(1) if dataclass else None,
            "fields": {row[0] for row in _rows(_subsection(body, "Fields"))},
            "indexes": {
                row[0]: (ast.literal_eval(row[1]), row[2] == "yes")
                for row in _rows(_subsection(body, "Indexes"))
            },
        }
    law_types = {row[0] for row in _rows(sections.get("LAW_TYPES", ""))}
    return collections, law_types


@pytest.fixture(scope="module")
def models():
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/patent_act_test")
    from db import models
    return models


@pytest.fixture(scope="module")
def doc():
    return parse_doc(DOC.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def live_indexes(models):
    """Indexes init_db() builds on an empty database, keyed by collection."""
    db = models.Database()
    assert db.db.name.endswith("_test"), f"drift test drops {db.db.name!r}; point MONGO_URI at a *_test database"
    db.client.drop_database(db.db.name)
    db.init_db()
    return {
        name: {
            index: (info["key"], bool(info.get("unique")))
            for index, info in db.db[name].index_information().items()
            if index != "_id_"
        }
        for name in db.db.list_collection_names()
    }


def test_indexes_match_doc(doc, live_indexes):
    collections, _ = doc
    problems = []
    for name in sorted(set(collections) | set(live_indexes)):
        live = live_indexes.get(name, {})
        if name not in collections:
            if live:
                problems.append(f"`{name}`: init_db() builds indexes {sorted(live)} but the doc has no `{name}` section")
            continue
        documented = collections[name]["indexes"]
        for index in sorted(set(documented) | set(live)):
            if documented.get(index) != live.get(index):
                problems.append(
                    f"`{name}`: index `{index}` is {documented.get(index)} in the doc but {live.get(index)} after init_db()"
                )
    assert not problems, _report(problems)


def test_law_types_match_doc(doc, models):
    _, law_types = doc
    code = set(models.LAW_TYPES)
    assert code == law_types, _report([
        f"LAW_TYPES: in code only {sorted(code - law_types)}, in the doc only {sorted(law_types - code)}"
    ])


def test_dataclass_fields_are_documented(doc, models):
    collections, _ = doc
    owner = {c["dataclass"]: name for name, c in collections.items() if c["dataclass"]}
    problems = []
    for cls in vars(models).values():
        if not (isinstance(cls, type) and dataclasses.is_dataclass(cls) and cls.__module__ == models.__name__):
            continue
        name = owner.get(cls.__name__)
        if name is None:
            problems.append(f"dataclass `{cls.__name__}` is not named by any collection's `Dataclass:` line")
            continue
        problems += [
            f"`{name}`: field `{f.name}` of `{cls.__name__}` is missing from the fields table"
            for f in dataclasses.fields(cls)
            if f.name not in collections[name]["fields"]
        ]
    assert not problems, _report(problems)
