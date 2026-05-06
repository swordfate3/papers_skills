import json

from shared.scripts.paper_workflow import setup_workspace, update_state


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
