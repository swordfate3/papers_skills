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
    run_web_workbench,
    web_workbench_status,
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


def test_run_web_workbench_executes_foreground_npm_command(monkeypatch):
    import paper_workflow

    calls = []

    class Result:
        returncode = 0

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return Result()

    monkeypatch.setattr(paper_workflow.subprocess, "run", fake_run)

    result = run_web_workbench("build")

    assert result["ok"] is True
    assert calls[0][0] == ["npm", "run", "build"]
    assert calls[0][1]["cwd"].name == "web"


def test_web_workbench_status_reports_stopped_when_no_state(tmp_path, monkeypatch):
    import paper_workflow

    state_path = tmp_path / "web-service.json"
    monkeypatch.setattr(paper_workflow, "web_service_state_path", lambda: state_path)

    status = web_workbench_status()

    assert status["running"] is False
    assert status["state_path"] == str(state_path)


def test_run_web_workbench_start_writes_state_and_launches_process(tmp_path, monkeypatch):
    import paper_workflow

    state_path = tmp_path / "web-service.json"
    calls = []

    class Process:
        pid = 4321

    def fake_popen(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return Process()

    monkeypatch.setattr(paper_workflow, "web_service_state_path", lambda: state_path)
    monkeypatch.setattr(paper_workflow.subprocess, "Popen", fake_popen)

    result = run_web_workbench("start", port=5179, host="127.0.0.1")

    assert result["ok"] is True
    assert result["pid"] == 4321
    assert result["url"] == "http://127.0.0.1:5179"
    assert calls[0][0] == ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5179"]
    assert state_path.exists()


def test_run_web_workbench_stop_removes_state_for_dead_process(tmp_path, monkeypatch):
    import paper_workflow

    state_path = tmp_path / "web-service.json"
    state_path.write_text('{"pid": 999999, "url": "http://127.0.0.1:5179"}', encoding="utf-8")
    monkeypatch.setattr(paper_workflow, "web_service_state_path", lambda: state_path)

    result = run_web_workbench("stop")

    assert result["ok"] is True
    assert result["running"] is False
    assert not state_path.exists()
