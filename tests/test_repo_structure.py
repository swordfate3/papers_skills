from pathlib import Path


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
