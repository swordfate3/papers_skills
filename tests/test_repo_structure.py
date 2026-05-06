from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_expected_top_level_directories_exist():
    for relative in [
        "skills/paper-research-workflow/scripts",
        "skills/paper-research-workflow/schemas",
        "skills/paper-research-workflow/templates",
        "skills/paper-research-workflow/references",
    ]:
        assert (ROOT / relative).is_dir()


def test_single_installable_skill_is_present():
    assert (ROOT / "skills/paper-research-workflow/SKILL.md").is_file()
    assert (ROOT / "skills/paper-research-workflow/agents/openai.yaml").is_file()


def test_only_one_discoverable_skill_exists():
    skill_files = sorted(path for path in (ROOT / "skills").glob("*/SKILL.md"))
    assert skill_files == [ROOT / "skills/paper-research-workflow/SKILL.md"]


def test_skill_frontmatter_has_name_and_description():
    skill_dir = ROOT / "skills/paper-research-workflow"
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert re.search(r"^name: " + re.escape(skill_dir.name) + r"$", text, re.MULTILINE)
    assert re.search(r"^description: .{40,}$", text, re.MULTILINE)
