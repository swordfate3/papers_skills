from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_expected_top_level_directories_exist():
    for relative in ["skills", "shared/scripts", "shared/schemas", "shared/templates"]:
        assert (ROOT / relative).is_dir()


def test_expected_skill_names_are_reserved():
    expected = {
        "paper-research-workflow",
        "paper-ingest-classifier",
        "paper-plain-explainer",
        "paper-expert-reader",
        "paper-code-reproducer",
        "paper-knowledge-base",
        "paper-innovation-miner",
    }
    actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
    assert expected <= actual


def test_skill_frontmatter_has_name_and_description():
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert re.search(r"^name: " + re.escape(skill_dir.name) + r"$", text, re.MULTILINE)
        assert re.search(r"^description: .{40,}$", text, re.MULTILINE)
