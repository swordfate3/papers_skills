from pathlib import Path

from shared.scripts.extract_pdf import default_mineru_wrapper


ROOT = Path(__file__).resolve().parents[1]


def test_pdf_reference_files_are_bundled():
    assert (ROOT / "shared/references/pdf-processing.md").is_file()
    assert (ROOT / "shared/references/mineru-local.md").is_file()


def test_default_mineru_wrapper_is_relative_to_repo():
    wrapper = default_mineru_wrapper()
    assert ".agents/skills" not in str(wrapper)
    assert wrapper == ROOT / "shared/scripts/mineru_to_md.sh"


def test_runtime_skill_bundle_does_not_reference_personal_skill_paths():
    text_suffixes = {".md", ".py", ".sh", ".json", ".yaml", ".yml"}
    for base in ["skills", "shared"]:
        for path in (ROOT / base).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in text_suffixes:
                assert ".agents/skills" not in path.read_text(encoding="utf-8")
