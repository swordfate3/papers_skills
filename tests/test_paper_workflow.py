import json
from pathlib import Path

from skills.paper_research_workflow_imports import SCRIPTS_DIR

import sys


if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from paper_workflow import (  # noqa: E402
    enable_local_mineru,
    load_default_workspace,
    local_mineru_status,
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


def test_local_mineru_status_marks_available_when_script_reports_ready(monkeypatch):
    import paper_workflow

    class Result:
        returncode = 0
        stdout = '{"docker_installed": true, "docker_daemon_running": true, "image_ready": true}'
        stderr = ""

    monkeypatch.setattr(paper_workflow.subprocess, "run", lambda *args, **kwargs: Result())

    status = local_mineru_status()
    assert status["available"] is True
    assert status["image_ready"] is True


def test_local_mineru_status_marks_unavailable_when_script_reports_not_ready(monkeypatch):
    import paper_workflow

    class Result:
        returncode = 1
        stdout = '{"docker_installed": true, "docker_daemon_running": false, "image_ready": false}'
        stderr = ""

    monkeypatch.setattr(paper_workflow.subprocess, "run", lambda *args, **kwargs: Result())

    status = local_mineru_status()
    assert status["available"] is False
    assert status["docker_daemon_running"] is False


def test_enable_local_mineru_passes_through_optional_sources(monkeypatch):
    import paper_workflow

    calls = []

    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return Result()

    monkeypatch.setattr(paper_workflow.subprocess, "run", fake_run)

    result = enable_local_mineru(
        docker_dir=Path("/tmp/mineru"),
        dockerfile_url="https://example.com/Dockerfile",
        source_archive_url="https://example.com/MinerU.tar.gz",
        source_subdir="docker/global",
        image="mineru:test",
    )

    assert result["ok"] is True
    assert calls[0][-10:] == [
        "--docker-dir",
        "/tmp/mineru",
        "--dockerfile-url",
        "https://example.com/Dockerfile",
        "--source-archive-url",
        "https://example.com/MinerU.tar.gz",
        "--source-subdir",
        "docker/global",
        "--image",
        "mineru:test",
    ]
