import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".claude/skills/ticket-system/scripts/generate_issues_index.py"
spec = importlib.util.spec_from_file_location("generate_issues_index", SCRIPT)
gen = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gen  # @dataclass resolves annotations via sys.modules
spec.loader.exec_module(gen)


def _count(section):
    return gen.count_open_questions(["## Details", "- not a question", "## Open Questions", *section, "## Related Files", "- `app.py`"])


def test_open_questions_cleared_by_none():
    assert _count(["", "- None.", ""]) == 0
    assert _count([]) == 0


def test_open_questions_counted_within_section_only():
    assert _count(["- Which model grades?", "- Cap per user?"]) == 2
