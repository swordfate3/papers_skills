from pathlib import Path

from skills.paper_research_workflow_imports import SCRIPTS_DIR

import sys


if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from extract_pdf import default_mineru_wrapper  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def test_pdf_reference_files_are_bundled():
    assert (ROOT / "skills/paper-research-workflow/references/pdf-processing.md").is_file()
    assert (ROOT / "skills/paper-research-workflow/references/mineru-local.md").is_file()


def test_default_mineru_wrapper_is_relative_to_repo():
    wrapper = default_mineru_wrapper()
    assert ".agents/skills" not in str(wrapper)
    assert wrapper == ROOT / "skills/paper-research-workflow/scripts/mineru_to_md.sh"


def test_runtime_skill_bundle_does_not_reference_personal_skill_paths():
    text_suffixes = {".md", ".py", ".sh", ".json", ".yaml", ".yml"}
    for path in (ROOT / "skills/paper-research-workflow").rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in text_suffixes:
                assert ".agents/skills" not in path.read_text(encoding="utf-8")
