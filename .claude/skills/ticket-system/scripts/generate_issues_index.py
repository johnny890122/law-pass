#!/usr/bin/env python3
"""Generate the docs/issues index, validate the ticket store, and file tickets.

Running this script does three things, in order:

1. Validates the store and exits non-zero on integrity errors: duplicate ids,
   malformed ids, stories whose id does not extend their parent epic id,
   unknown statuses, completed epics with active stories, `in_progress` or
   `resolved` tickets that still list Open Questions, or filing moves that
   would overwrite an existing file.
2. Files every ticket into its status folder. Standalone tickets and epic files
   live directly under `<status>/`; stories live under
   `<status>/<epic-folder>/`. Parent epics and their stories may therefore live
   in different status folders while work is in flight. Reopened tickets move
   back to `pending/` or `in_progress/` on the next run. Ticket-specific image
   folders at `img/<lowercase-ticket-id>/` move with their ticket.
3. Writes the index: a slim `README.md` landing page, one overview per status
   group -- `in-progress.md`, `pending.md`, `done.md` -- plus
   `closure-debt.md`, which lists completed tickets that still have unchecked
   acceptance criteria, no `## Resolution` section, or no resolved date. That
   page should stay empty.

The parser intentionally supports only the small YAML subset used by issue
tickets, so this script has no dependency beyond the Python standard library.
"""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ROOT = SKILL_ROOT.parents[2]  # repo root: .../.claude/skills/ticket-system -> repo
ISSUES_DIR = ROOT / "docs" / "issues"
README = ISSUES_DIR / "README.md"

# Per-status overview pages written next to the README.
OVERVIEW_FILES = {
    "in_progress": ISSUES_DIR / "in-progress.md",
    "pending": ISSUES_DIR / "pending.md",
    "done": ISSUES_DIR / "done.md",
    "closure_debt": ISSUES_DIR / "closure-debt.md",
}
EXCLUDED = {"README.md", *(p.name for p in OVERVIEW_FILES.values())}

# Canonical statuses, listed in the order they should appear in the index.
STATUS_ORDER = ["in_progress", "pending", "resolved", "wont_fix"]
# Free-form status values seen in hand-written tickets, mapped to canonical ones.
STATUS_ALIASES = {"in-progress": "in_progress", "done": "resolved"}
# Completed statuses, shown together in the done overview.
COMPLETED_STATUSES = ["resolved", "wont_fix"]
# Every canonical status has a matching ticket folder.
STATUS_DIRS = {status: ISSUES_DIR / status for status in STATUS_ORDER}

ID_PATTERN = re.compile(r"^LP-\d{4}(-\d{2})?$")
# Statuses that mean implementation has started: Open Questions must be cleared.
CLEARED_QUESTION_STATUSES = {"in_progress", "resolved"}

GEN_NOTE = (
    "> Generated from ticket frontmatter by "
    "`.claude/skills/ticket-system/scripts/generate_issues_index.py`. "
    "Do not edit by hand."
)
GEN_COMMAND = (
    "python3 .claude/skills/ticket-system/scripts/generate_issues_index.py"
)

TYPE_LABELS = {
    "bug": "[BUG]",
    "feature": "[FEATURE]",
    "improvement": "[IMPROVEMENT]",
    "refactor": "[REFACTOR]",
    "todo": "[TODO]",
    "epic": "[EPIC]",
    "story": "[STORY]",
}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Ticket:
    path: Path
    metadata: dict[str, str | list[str]]
    unchecked_ac: int = 0
    has_resolution: bool = False
    open_questions: int = 0

    @property
    def rel_link(self) -> str:
        return f"./{self.path.relative_to(ISSUES_DIR).as_posix()}"

    @property
    def id(self) -> str:
        return str(self.metadata.get("id", ""))

    @property
    def title(self) -> str:
        return str(self.metadata.get("title", self.path.stem))

    @property
    def type(self) -> str:
        return str(self.metadata.get("type", "todo")).lower()

    @property
    def raw_status(self) -> str:
        return str(self.metadata.get("status", "pending")).lower()

    @property
    def status(self) -> str:
        return STATUS_ALIASES.get(self.raw_status, self.raw_status)

    @property
    def is_completed(self) -> bool:
        return self.status in COMPLETED_STATUSES

    @property
    def priority(self) -> str:
        return str(self.metadata.get("priority", "medium")).lower()

    @property
    def area(self) -> str:
        return str(self.metadata.get("area", "general"))

    @property
    def created(self) -> str:
        return str(self.metadata.get("created", ""))

    @property
    def resolved(self) -> str:
        return str(self.metadata.get("resolved", "") or "")

    @property
    def parent(self) -> str:
        return str(self.metadata.get("parent", "") or "")


def parse_frontmatter(lines: list[str], path: Path) -> dict[str, str | list[str]]:
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path} is missing frontmatter")

    metadata: dict[str, str | list[str]] = {}
    current_list_key: str | None = None

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return metadata

        if current_list_key and stripped.startswith("- "):
            value = stripped[2:].strip()
            cast_list = metadata.setdefault(current_list_key, [])
            if isinstance(cast_list, list):
                cast_list.append(value)
            continue

        current_list_key = None
        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value == "":
            metadata[key] = ""
            current_list_key = key
        else:
            metadata[key] = value.strip('"').strip("'")

    raise ValueError(f"{path} frontmatter is not closed")


def count_open_questions(lines: list[str]) -> int:
    """Non-empty lines under `## Open Questions`. `None` or an empty section is cleared."""
    count, inside = 0, False
    for line in lines:
        if line.startswith("## "):
            inside = line.strip() == "## Open Questions"
            continue
        text = line.strip().lstrip("-* ").strip().rstrip(".")
        if inside and text and text.lower() != "none":
            count += 1
    return count


def load_ticket(path: Path) -> Ticket:
    lines = path.read_text(encoding="utf-8").splitlines()
    metadata = parse_frontmatter(lines, path)
    unchecked = sum(1 for line in lines if line.lstrip().startswith("- [ ]"))
    has_resolution = any(line.strip().startswith("## Resolution") for line in lines)
    return Ticket(
        path=path,
        metadata=metadata,
        unchecked_ac=unchecked,
        has_resolution=has_resolution,
        open_questions=count_open_questions(lines),
    )


def load_tickets() -> list[Ticket]:
    # Standalone tickets and epic files live directly in a status folder.
    # Stories live one level deeper, in a folder named after their epic file.
    return [
        load_ticket(path)
        for path in sorted(ISSUES_DIR.rglob("*.md"))
        if path.name not in EXCLUDED
    ]


def validate(tickets: list[Ticket]) -> list[str]:
    """Return a list of integrity errors. Any error blocks filing and indexing."""
    errors: list[str] = []
    by_id: dict[str, list[Ticket]] = {}
    for ticket in tickets:
        by_id.setdefault(ticket.id, []).append(ticket)

    for ticket_id, group in sorted(by_id.items()):
        if len(group) > 1:
            paths = ", ".join(str(t.path.relative_to(ROOT)) for t in group)
            errors.append(f"duplicate id {ticket_id}: {paths}")

    epics_by_id = {t.id: t for t in tickets if not t.parent}
    children_by_parent: dict[str, list[Ticket]] = {}
    for ticket in tickets:
        rel = ticket.path.relative_to(ROOT)
        if not ticket.id:
            errors.append(f"{rel}: missing id")
        elif not ID_PATTERN.match(ticket.id):
            errors.append(
                f"{rel}: id {ticket.id!r} does not match LP-XXXX / LP-XXXX-YY"
            )
        if ticket.status not in STATUS_ORDER:
            errors.append(f"{rel}: unknown status {ticket.raw_status!r}")
        if ticket.status in CLEARED_QUESTION_STATUSES and ticket.open_questions:
            errors.append(
                f"{rel}: {ticket.open_questions} open question(s) must be cleared "
                f"(write `- None.`) before status {ticket.status}"
            )
        if ticket.parent:
            children_by_parent.setdefault(ticket.parent, []).append(ticket)
            if ticket.parent not in epics_by_id:
                errors.append(f"{rel}: parent {ticket.parent} not found")
            elif not ticket.id.startswith(f"{ticket.parent}-"):
                errors.append(
                    f"{rel}: story id {ticket.id} does not extend "
                    f"parent id {ticket.parent}"
                )
    for epic_id, children in sorted(children_by_parent.items()):
        epic = epics_by_id.get(epic_id)
        if epic and epic.is_completed:
            active = [child.id for child in children if not child.is_completed]
            if active:
                errors.append(
                    f"{epic.path.relative_to(ROOT)}: completed epic has active "
                    f"stories: {', '.join(active)}"
                )
    return errors


def target_dir(ticket: Ticket, epics_by_id: dict[str, Ticket]) -> Path | None:
    """Where this ticket file should live. None when it cannot be determined."""
    if ticket.parent:
        epic = epics_by_id.get(ticket.parent)
        if epic is None:
            return None
        return STATUS_DIRS[ticket.status] / epic.path.stem

    return STATUS_DIRS[ticket.status]


def _find_non_directory_ancestor(path: Path) -> Path | None:
    candidate = path
    while candidate != ISSUES_DIR.parent:
        if candidate.exists():
            return None if candidate.is_dir() else candidate
        candidate = candidate.parent
    return None


def file_by_status(tickets: list[Ticket]) -> tuple[int, list[str]]:
    """Move each ticket to its status-derived location after collision preflight."""
    epics_by_id = {t.id: t for t in tickets if not t.parent}

    move_plan: list[tuple[Ticket, Path, Path, Path]] = []
    errors: list[str] = []
    planned_destinations: dict[Path, Ticket] = {}
    for status_dir in STATUS_DIRS.values():
        blocked_by = _find_non_directory_ancestor(status_dir)
        if blocked_by:
            errors.append(
                f"filing collision: required status path "
                f"{status_dir.relative_to(ROOT)} is blocked by non-directory "
                f"{blocked_by.relative_to(ROOT)}"
            )
    for ticket in tickets:
        dest_dir = target_dir(ticket, epics_by_id)
        if dest_dir is None or ticket.path.parent == dest_dir:
            continue
        dest = dest_dir / ticket.path.name
        asset_source = ticket.path.parent / "img" / ticket.id.lower()
        asset_dest = dest_dir / "img" / ticket.id.lower()
        blocked_by = _find_non_directory_ancestor(dest.parent)
        if blocked_by:
            errors.append(
                f"filing collision: {dest.relative_to(ROOT)} is blocked by "
                f"non-directory {blocked_by.relative_to(ROOT)}"
            )
            continue
        previous = planned_destinations.get(dest)
        if previous:
            errors.append(
                f"filing collision: {ticket.path.relative_to(ROOT)} and "
                f"{previous.path.relative_to(ROOT)} both target "
                f"{dest.relative_to(ROOT)}"
            )
            continue
        planned_destinations[dest] = ticket
        if dest.exists():
            errors.append(
                f"filing collision: {ticket.path.relative_to(ROOT)} -> "
                f"{dest.relative_to(ROOT)} already exists"
            )
            continue
        if asset_source.exists() and asset_dest.exists():
            errors.append(
                f"filing collision: {asset_source.relative_to(ROOT)} -> "
                f"{asset_dest.relative_to(ROOT)} already exists"
            )
            continue
        move_plan.append((ticket, dest, asset_source, asset_dest))

    if errors:
        return 0, errors

    moved = 0
    for ticket, dest, asset_source, asset_dest in move_plan:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ticket.path), str(dest))
        print(f"filed: {ticket.path.relative_to(ROOT)} -> {dest.relative_to(ROOT)}")
        if asset_source.exists():
            asset_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(asset_source), str(asset_dest))
            print(
                f"filed assets: {asset_source.relative_to(ROOT)} -> "
                f"{asset_dest.relative_to(ROOT)}"
            )
        moved += 1

    for status_dir in STATUS_DIRS.values():
        status_dir.mkdir(parents=True, exist_ok=True)
    _remove_empty_dirs(ISSUES_DIR)
    return moved, errors


def _remove_empty_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path in STATUS_DIRS.values():
            continue
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def sort_key(ticket: Ticket) -> tuple[int, int, str, str]:
    status_rank = (
        STATUS_ORDER.index(ticket.status)
        if ticket.status in STATUS_ORDER
        else len(STATUS_ORDER)
    )
    priority_rank = PRIORITY_ORDER.get(ticket.priority, 99)
    return (status_rank, priority_rank, ticket.created, ticket.id)


def order_with_stories(tickets: list[Ticket]) -> list[Ticket]:
    """Sort tickets, then move each story directly under its parent epic."""
    ordered = sorted(tickets, key=sort_key)
    stories_by_parent: dict[str, list[Ticket]] = {}
    top_level: list[Ticket] = []
    for ticket in ordered:
        if ticket.parent:
            stories_by_parent.setdefault(ticket.parent, []).append(ticket)
        else:
            top_level.append(ticket)

    result: list[Ticket] = []
    for ticket in top_level:
        result.append(ticket)
        result.extend(stories_by_parent.pop(ticket.id, []))
    # Stories whose parent epic sits in another status section.
    for stories in stories_by_parent.values():
        result.extend(stories)
    return result


def status_heading(status: str) -> str:
    return {
        "pending": "Pending",
        "in_progress": "In Progress",
        "resolved": "Resolved",
        "wont_fix": "Won't Fix",
    }.get(status, status.replace("_", " ").title())


def render_table(
    tickets: list[Ticket],
    include_resolved: bool = False,
    epics_by_id: dict[str, Ticket] | None = None,
) -> list[str]:
    if not tickets:
        return ["No tickets."]

    lines = [
        "| ID | Type | Priority | Area | Parent | Title | Created | Resolved |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for ticket in tickets:
        type_label = TYPE_LABELS.get(ticket.type, f"[{ticket.type.upper()}]")
        resolved = ticket.resolved if include_resolved else "-"
        parent = "-"
        if ticket.parent:
            epic = (epics_by_id or {}).get(ticket.parent)
            parent = f"[{ticket.parent}]({epic.rel_link})" if epic else ticket.parent
        lines.append(
            "| "
            f"{ticket.id} | "
            f"{type_label} | "
            f"{ticket.priority.title()} | "
            f"{ticket.area} | "
            f"{parent} | "
            f"[{ticket.title}]({ticket.rel_link}) | "
            f"{ticket.created or '-'} | "
            f"{resolved or '-'} |"
        )
    return lines


def completed_sorted(tickets: list[Ticket], status: str) -> list[Ticket]:
    return sorted(
        [ticket for ticket in tickets if ticket.status == status],
        key=lambda ticket: (ticket.resolved or ticket.created, ticket.id),
        reverse=True,
    )


def render_active_page(tickets: list[Ticket], status: str) -> str:
    status_tickets = order_with_stories([t for t in tickets if t.status == status])
    epics_by_id = {ticket.id: ticket for ticket in tickets if not ticket.parent}
    lines = [f"# {status_heading(status)}", "", GEN_NOTE, ""]
    lines.extend(render_table(status_tickets, epics_by_id=epics_by_id))
    lines.append("")
    return "\n".join(lines)


def render_done_page(tickets: list[Ticket]) -> str:
    lines = ["# Done", "", GEN_NOTE, ""]
    epics_by_id = {ticket.id: ticket for ticket in tickets if not ticket.parent}
    for index, status in enumerate(COMPLETED_STATUSES):
        lines.extend([f"## {status_heading(status)}", ""])
        lines.extend(
            render_table(
                completed_sorted(tickets, status),
                include_resolved=True,
                epics_by_id=epics_by_id,
            )
        )
        if index < len(COMPLETED_STATUSES) - 1:
            lines.append("")
    return "\n".join(lines) + "\n"


def closure_debt(tickets: list[Ticket]) -> list[tuple[Ticket, list[str]]]:
    """Completed tickets whose closure is incomplete for handover purposes."""
    debts: list[tuple[Ticket, list[str]]] = []
    for ticket in sorted((t for t in tickets if t.is_completed), key=lambda t: t.id):
        problems = []
        if ticket.unchecked_ac:
            problems.append(f"{ticket.unchecked_ac} unchecked AC box(es)")
        if not ticket.has_resolution:
            problems.append("no `## Resolution` section")
        if not ticket.resolved:
            problems.append("no resolved date")
        if problems:
            debts.append((ticket, problems))
    return debts


def render_closure_debt_page(tickets: list[Ticket]) -> str:
    debts = closure_debt(tickets)
    lines = [
        "# Closure Debt",
        "",
        GEN_NOTE,
        "",
        "Completed tickets whose closure is incomplete: unchecked acceptance",
        "criteria (often the `Docs synced` box), a missing `## Resolution`",
        "section, or a missing resolved date. This list should stay empty.",
        "",
    ]
    if not debts:
        lines.extend(
            ["No closure debt. All completed tickets are fully closed.", ""]
        )
        return "\n".join(lines)

    lines.extend(["| ID | Title | Problems |", "| --- | --- | --- |"])
    for ticket, problems in debts:
        lines.append(
            f"| {ticket.id} | [{ticket.title}]({ticket.rel_link}) | "
            f"{'; '.join(problems)} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_readme(tickets: list[Ticket]) -> str:
    counts = {
        status: sum(1 for t in tickets if t.status == status)
        for status in STATUS_ORDER
    }
    done_total = counts["resolved"] + counts["wont_fix"]
    debt_count = len(closure_debt(tickets))
    return "\n".join(
        [
            "# Issues",
            "",
            "Stage 1 of the ticket-first workflow in [CLAUDE.md](../../CLAUDE.md):",
            "every non-trivial change starts as a ticket here.",
            "",
            GEN_NOTE,
            f"> Run `{GEN_COMMAND}` from the repo root to refresh after editing "
            "ticket frontmatter.",
            "",
            "## Status Overviews",
            "",
            f"- [In Progress](./in-progress.md) — {counts['in_progress']}",
            f"- [Pending](./pending.md) — {counts['pending']}",
            f"- [Done](./done.md) — {done_total} (resolved {counts['resolved']}, "
            f"won't-fix {counts['wont_fix']})",
            f"- [Closure Debt](./closure-debt.md) — {debt_count} completed "
            "ticket(s) not fully closed",
            "",
            "## Folder Layout",
            "",
            "- Every ticket is filed under the folder matching its canonical "
            "status: `pending/`, `in_progress/`, `resolved/`, or `wont_fix/`.",
            "- Standalone tickets and epic files live directly in their status "
            "folder. Stories live in `<status>/<epic-folder>/`.",
            "- A story is filed by its own status, independently of its parent "
            "epic. Mixed-status epics therefore have matching epic folders under "
            "more than one status.",
            "- Ticket-specific images live at "
            "`<ticket-parent>/img/<lowercase-ticket-id>/` so the generator can "
            "move them with the ticket.",
            "- The filing is automated: change the `status` field, rerun the "
            "generator, and it moves the file. Never move ticket files by hand.",
            "",
            "## Ticket Metadata",
            "",
            "Tickets are Markdown files with YAML frontmatter. Filenames are "
            "stable and do not change when status changes; use the `status` "
            "field instead.",
            "",
            "| Field | Values / Format | Notes |",
            "| --- | --- | --- |",
            "| `id` | `LP-0001` | Stable ticket identifier. Take the highest id "
            "across every status folder and increment. The generator fails on "
            "duplicates. |",
            "| `title` | Text | Human-readable ticket title. |",
            "| `type` | `bug`, `feature`, `improvement`, `refactor`, `todo`, "
            "`epic`, `story` | Work category. Epics group story tickets. |",
            "| `status` | `pending`, `in_progress`, `resolved`, `wont_fix` | "
            "Drives the overviews and which folder the ticket is filed in. |",
            "| `priority` | `high`, `medium`, `low` | Used for sorting within "
            "status. |",
            "| `created` | `YYYY-MM-DD` | Creation date. |",
            "| `resolved` | `YYYY-MM-DD` or blank | Fill when resolved. |",
            "| `area` | Short slug | Example: `quiz`, `question-gen`, `grading`, "
            "`laws`, `auth`, `ui`, `db`, `docs`. |",
            "| `parent` | `LP-XXXX` or blank | Stories only: id of the parent "
            "epic. Story ids extend the epic id (`LP-XXXX-01`), and story files "
            "live in a folder named after the epic file. |",
            "| `tags` | YAML list | Optional discovery labels. |",
            "",
            "Use `.claude/skills/ticket-system/assets/TICKET_TEMPLATE.md` when "
            "creating a new ticket.",
            "",
        ]
    )


def main() -> None:
    ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    tickets = load_tickets()

    errors = validate(tickets)
    if errors:
        print("ticket store validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    moved, move_errors = file_by_status(tickets)
    if move_errors:
        print("filing failed:", file=sys.stderr)
        for error in move_errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    tickets = load_tickets()  # reload so links reflect filed paths

    README.write_text(render_readme(tickets), encoding="utf-8")
    OVERVIEW_FILES["in_progress"].write_text(
        render_active_page(tickets, "in_progress"), encoding="utf-8"
    )
    OVERVIEW_FILES["pending"].write_text(
        render_active_page(tickets, "pending"), encoding="utf-8"
    )
    OVERVIEW_FILES["done"].write_text(render_done_page(tickets), encoding="utf-8")
    OVERVIEW_FILES["closure_debt"].write_text(
        render_closure_debt_page(tickets), encoding="utf-8"
    )

    debt = len(closure_debt(tickets))
    print(
        f"Generated index from {len(tickets)} tickets "
        f"({moved} filed by status, {debt} with closure debt)"
    )


if __name__ == "__main__":
    main()
