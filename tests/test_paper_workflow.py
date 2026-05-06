import json

from skills.paper_research_workflow_imports import SCRIPTS_DIR

import sys


if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from paper_workflow import (  # noqa: E402
    load_default_workspace,
    save_default_workspace,
    setup_workspace,
    update_state,
)


def test_setup_workspace_creates_expected_directories(tmp_path):
    workspace = tmp_path / "workspace"
    setup_workspace(workspace)
    for relative in [
        "inbox",
        "papers/by-domain",
        "papers/by-year",
        "papers/by-venue",
        "extracted",
        "knowledge/papers",
        "knowledge/cards",
        "knowledge/expert-readings",
        "knowledge/reproductions",
        "knowledge/innovations",
        "state",
    ]:
        assert (workspace / relative).exists()


def test_update_state_records_stage(tmp_path):
    workspace = tmp_path / "workspace"
    setup_workspace(workspace)
    update_state(workspace, "paper-1", "ingested", {"path": "x.pdf"})
    data = json.loads((workspace / "state/papers.json").read_text(encoding="utf-8"))
    assert data["papers"]["paper-1"]["stages"]["ingested"]["path"] == "x.pdf"


def test_save_and_load_default_workspace(tmp_path):
    config = tmp_path / ".paper-workspace.json"
    workspace = tmp_path / "paper-library"
    save_default_workspace(workspace, config)
    assert load_default_workspace(config) == workspace.resolve()
