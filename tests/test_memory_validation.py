import json
from pathlib import Path

from shared.scripts.paper_research_common import make_paper_id, normalize_slug, read_json, write_json
from shared.scripts.validate_memory import validate_memory


ROOT = Path(__file__).resolve().parents[1]


def test_normalize_slug_is_ascii_stable():
    assert normalize_slug("Attention Is All You Need!") == "attention-is-all-you-need"
    assert normalize_slug("  A/B: Test_of Systems  ") == "a-b-test-of-systems"


def test_make_paper_id_is_stable_and_short():
    first = make_paper_id("Attention Is All You Need", 2017)
    second = make_paper_id("Attention Is All You Need", 2017)
    assert first == second
    assert first.startswith("2017-attention-is-all-you-need-")
    assert len(first.rsplit("-", 1)[-1]) == 6


def test_read_write_json_round_trip(tmp_path):
    path = tmp_path / "nested" / "data.json"
    write_json(path, {"a": 1})
    assert read_json(path) == {"a": 1}


def test_validate_memory_accepts_template():
    memory = json.loads((ROOT / "shared/templates/paper-memory.json").read_text(encoding="utf-8"))
    errors = validate_memory(memory, ROOT / "shared/schemas/paper-memory.schema.json")
    assert errors == []


def test_validate_memory_reports_missing_required_field():
    memory = json.loads((ROOT / "shared/templates/paper-memory.json").read_text(encoding="utf-8"))
    del memory["paper_id"]
    errors = validate_memory(memory, ROOT / "shared/schemas/paper-memory.schema.json")
    assert any("paper_id" in error for error in errors)
