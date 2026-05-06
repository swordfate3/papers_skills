import json
from pathlib import Path

from skills.paper_research_workflow_imports import SCRIPTS_DIR

import sys


if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from kb_query import load_memories, rank_related_papers  # noqa: E402
from paper_workflow import setup_workspace  # noqa: E402
from validate_memory import validate_memory  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def test_fixture_memories_validate():
    schema = ROOT / "skills/paper-research-workflow/schemas/paper-memory.schema.json"
    for path in sorted((ROOT / "tests/fixtures/memory").glob("*.json")):
        errors = validate_memory(json.loads(path.read_text(encoding="utf-8")), schema)
        assert errors == []


def test_kb_query_loads_fixture_memories(tmp_path):
    workspace = tmp_path / "workspace"
    setup_workspace(workspace)
    kb_dir = workspace / "knowledge/papers"
    for fixture in (ROOT / "tests/fixtures/memory").glob("*.json"):
        (kb_dir / fixture.name).write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
    memories = load_memories(kb_dir)
    assert len(memories) == 2
    ranked = rank_related_papers(memories[0], memories[1:])
    assert ranked
    assert ranked[0]["score"] >= 0
