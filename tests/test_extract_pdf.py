from skills.paper_research_workflow_imports import SCRIPTS_DIR

import sys


if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from extract_pdf import (  # noqa: E402
    ExtractionMetrics,
    choose_extraction_strategy,
    normalize_mineru_outputs,
    resolve_mineru_backend,
)


def test_choose_lightweight_for_good_text_pdf():
    metrics = ExtractionMetrics(chars=20000, pages=8, table_markers=2, formula_markers=3)
    assert choose_extraction_strategy(metrics) == "lightweight"


def test_choose_mineru_for_too_little_text():
    metrics = ExtractionMetrics(chars=100, pages=10, table_markers=0, formula_markers=0)
    assert choose_extraction_strategy(metrics) == "mineru"


def test_choose_mineru_for_formula_heavy_pdf():
    metrics = ExtractionMetrics(chars=12000, pages=6, table_markers=1, formula_markers=80)
    assert choose_extraction_strategy(metrics) == "mineru"


def test_normalize_mineru_outputs_picks_markdown_file(tmp_path):
    mineru_dir = tmp_path / "mineru"
    mineru_dir.mkdir()
    (mineru_dir / "full.md").write_text("# Paper\n\ncontent", encoding="utf-8")
    output_dir = tmp_path / "out"
    manifest = normalize_mineru_outputs(mineru_dir, output_dir)
    assert (output_dir / "text.md").read_text(encoding="utf-8").startswith("# Paper")
    assert manifest["strategy"] == "mineru"


def test_auto_backend_prefers_custom_wrapper(monkeypatch, tmp_path):
    wrapper = tmp_path / "mineru-wrapper.sh"
    wrapper.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    monkeypatch.setenv("MINERU_TO_MD", str(wrapper))
    monkeypatch.setenv("MINERU_TOKEN", "token")

    assert resolve_mineru_backend("auto") == "custom"


def test_auto_backend_uses_standard_cloud_when_token_exists(monkeypatch):
    monkeypatch.delenv("MINERU_TO_MD", raising=False)
    monkeypatch.setenv("MINERU_TOKEN", "token")

    assert resolve_mineru_backend("auto") == "standard-cloud"


def test_auto_backend_uses_saved_standard_token(monkeypatch, tmp_path):
    import extract_pdf
    from mineru_cloud import save_mineru_config

    config_path = tmp_path / ".paper-mineru.json"
    save_mineru_config("saved-token", config_path)
    monkeypatch.delenv("MINERU_TO_MD", raising=False)
    monkeypatch.delenv("MINERU_TOKEN", raising=False)
    monkeypatch.setattr(extract_pdf, "default_mineru_config_path", lambda: config_path)

    assert resolve_mineru_backend("auto") == "standard-cloud"


def test_explicit_standard_cloud_backend_is_preserved(monkeypatch):
    monkeypatch.delenv("MINERU_TO_MD", raising=False)
    monkeypatch.delenv("MINERU_TOKEN", raising=False)

    assert resolve_mineru_backend("standard-cloud") == "standard-cloud"
