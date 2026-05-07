import json
from pathlib import Path

from skills.paper_research_workflow_imports import SCRIPTS_DIR

import sys


if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from paper_workflow import (  # noqa: E402
    enable_local_mineru,
    export_web_workbench_data,
    load_default_workspace,
    local_mineru_status,
    release_web_workbench,
    run_web_workbench,
    web_workbench_dir,
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
    assert (workspace / "web/package.json").is_file()
    assert (workspace / "web/src/App.tsx").is_file()


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

    result = run_web_workbench("build", workspace=Path("/tmp/paper-workspace"))

    assert result["ok"] is True
    assert calls[0][0] == ["npm", "run", "build"]
    assert calls[0][1]["cwd"] == Path("/tmp/paper-workspace/web")


def test_web_workbench_status_reports_stopped_when_no_state(tmp_path, monkeypatch):
    import paper_workflow

    state_path = tmp_path / "web-service.json"
    monkeypatch.setattr(paper_workflow, "web_service_state_path", lambda workspace=None: state_path)

    status = web_workbench_status(tmp_path)

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

    monkeypatch.setattr(paper_workflow, "web_service_state_path", lambda workspace=None: state_path)
    monkeypatch.setattr(paper_workflow.subprocess, "Popen", fake_popen)

    result = run_web_workbench("start", workspace=tmp_path, port=5179, host="127.0.0.1")

    assert result["ok"] is True
    assert result["pid"] == 4321
    assert result["url"] == "http://127.0.0.1:5179"
    assert calls[0][0] == ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5179"]
    assert calls[0][1]["cwd"] == tmp_path / "web"
    assert state_path.exists()


def test_run_web_workbench_stop_removes_state_for_dead_process(tmp_path, monkeypatch):
    import paper_workflow

    state_path = tmp_path / "web-service.json"
    state_path.write_text('{"pid": 999999, "url": "http://127.0.0.1:5179"}', encoding="utf-8")
    monkeypatch.setattr(paper_workflow, "web_service_state_path", lambda workspace=None: state_path)

    result = run_web_workbench("stop", workspace=tmp_path)

    assert result["ok"] is True
    assert result["running"] is False
    assert not state_path.exists()


def test_release_web_workbench_copies_template_to_workspace(tmp_path):
    workspace = tmp_path / "paper-library"
    target = release_web_workbench(workspace)

    assert target == workspace / "web"
    assert (target / "package.json").is_file()
    assert (target / "src/App.tsx").is_file()
    assert web_workbench_dir(workspace) == target


def test_release_web_workbench_syncs_template_updates_without_runtime_dirs(tmp_path):
    workspace = tmp_path / "paper-library"
    target = release_web_workbench(workspace)
    stale_file = target / "src/workbenchData.ts"
    stale_file.write_text("stale", encoding="utf-8")
    runtime_file = target / "node_modules/local.txt"
    runtime_file.parent.mkdir()
    runtime_file.write_text("keep", encoding="utf-8")

    release_web_workbench(workspace)

    assert "WORKBENCH_DATA_URL" in stale_file.read_text(encoding="utf-8")
    assert runtime_file.read_text(encoding="utf-8") == "keep"


def test_export_web_workbench_data_writes_hot_json_from_workspace(tmp_path):
    workspace = tmp_path / "paper-library"
    setup_workspace(workspace)
    memory = {
        "paper_id": "paper-1",
        "title": "Differential Equation Paper",
        "year": 2026,
        "classification": {
            "domains": ["差分论文"],
            "keywords": ["difference", "equation"],
        },
        "status": {"ingested": True},
    }
    memory_path = workspace / "knowledge/papers/paper-1.json"
    memory_path.write_text(json.dumps(memory), encoding="utf-8")
    (workspace / "knowledge/cards/paper-1.md").write_text("# 通俗解释\n\n核心直觉 A\n\n- 要点一\n- 要点二\n", encoding="utf-8")
    (workspace / "knowledge/expert-readings/paper-1.md").write_text("# 专家阅读\n\n实验缺陷 B\n", encoding="utf-8")
    (workspace / "knowledge/reproductions/paper-1.md").write_text("# 复现计划\n\n先做最小实验 C\n", encoding="utf-8")
    (workspace / "knowledge/innovations/idea-1.md").write_text(
        "# 新想法\n\nscore: 88\nrank: 1\nsources: paper-1\n\n把差分结构用于算子学习。",
        encoding="utf-8",
    )

    data_path = export_web_workbench_data(workspace)
    payload = json.loads(data_path.read_text(encoding="utf-8"))

    assert data_path == workspace / "web/public/paper-workbench-data.json"
    assert payload["papers"][0]["id"] == "paper-1"
    assert payload["papers"][0]["category"] == "差分论文"
    assert payload["papers"][0]["cards"]["plain"]["summary"].startswith("核心直觉")
    assert payload["innovations"][0]["score"] == 88


def test_run_web_workbench_refresh_data_command_writes_hot_json(tmp_path):
    workspace = tmp_path / "paper-library"
    result = run_web_workbench("refresh-data", workspace=workspace)

    assert result["ok"] is True
    assert result["data_path"] == str(workspace / "web/public/paper-workbench-data.json")
    assert (workspace / "web/public/paper-workbench-data.json").is_file()
