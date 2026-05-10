import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/paper-research-workflow"


def test_single_skill_directory_contains_all_runtime_resources():
    for relative in [
        "SKILL.md",
        "agents/openai.yaml",
        "scripts/paper_workflow.py",
        "scripts/extract_pdf.py",
        "scripts/mineru_cloud.py",
        "scripts/mineru_to_md.sh",
        "scripts/mineru_local_docker.sh",
        "schemas/paper-memory.schema.json",
        "schemas/web-workbench-data.schema.json",
        "templates/paper-memory.json",
        "references/pdf-processing.md",
        "references/mineru-local.md",
        "references/child-skills/paper-ingest-classifier.md",
        "references/child-skills/paper-innovation-miner.md",
        "references/child-skills/paper-web-workbench.md",
        "web/package.json",
        "web/index.html",
        "web/src/App.tsx",
        "web/src/domain.ts",
        "web/src/MarkdownReader.tsx",
        "web/src/workbenchData.ts",
        "web/src/promptBuilder.ts",
        "web/src/App.test.tsx",
        "web/public/paper-workbench-data.json",
    ]:
        assert (SKILL_DIR / relative).is_file()


def test_visual_workbench_declares_expected_frontend_stack():
    package = (SKILL_DIR / "web/package.json").read_text(encoding="utf-8")
    assert '"react"' in package
    assert '"vite"' in package
    assert '"test"' in package
    assert '"build"' in package


def test_visual_workbench_template_contains_no_sample_data_or_build_outputs():
    forbidden_files = [
        "web/src/sampleData.ts",
        "web/package-lock.json",
        "web/tsconfig.tsbuildinfo",
        "web/dist/index.html",
    ]
    for relative in forbidden_files:
        assert not (SKILL_DIR / relative).exists()

    forbidden_patterns = [
        "sampleData",
        "sampleWorkbenchData",
        "dataOrSample",
        "2024-differential-transformer",
        "a1b2c3",
        "Differential Transformer",
        "Integral Operator",
    ]
    for path in (SKILL_DIR / "web").rglob("*"):
        if path.is_file() and path.suffix in {".ts", ".tsx", ".js", ".json"}:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden_patterns:
                assert pattern not in text, f"{pattern!r} found in {path}"


def test_single_skill_install_smoke_test(tmp_path):
    installed = tmp_path / "paper-research-workflow"
    shutil.copytree(SKILL_DIR, installed)
    workspace = tmp_path / "workspace"

    setup = subprocess.run(
        [sys.executable, "scripts/paper_workflow.py", "setup", "--workspace", str(workspace)],
        cwd=installed,
        check=False,
        capture_output=True,
        text=True,
    )
    assert setup.returncode == 0, setup.stderr
    assert (workspace / "state/papers.json").is_file()
    setup_payload = json.loads(setup.stdout)
    assert setup_payload["ok"] is True
    assert setup_payload["workspace"] == str(workspace.resolve())
    assert any("读取论文" in action for action in setup_payload["next_actions"])

    status = subprocess.run(
        [sys.executable, "scripts/paper_workflow.py", "status", "--workspace", str(workspace)],
        cwd=installed,
        check=False,
        capture_output=True,
        text=True,
    )
    assert status.returncode == 0, status.stderr
    assert '"papers": {}' in status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["ok"] is True
    assert status_payload["workspace"] == str(workspace.resolve())
    assert any("启动可视化" in action for action in status_payload["next_actions"])


def test_single_skill_mineru_config_smoke_test(tmp_path):
    installed = tmp_path / "paper-research-workflow"
    shutil.copytree(SKILL_DIR, installed)

    configure = subprocess.run(
        [
            sys.executable,
            "scripts/paper_workflow.py",
            "configure-mineru",
            "--standard-token",
            "test-token",
        ],
        cwd=installed,
        check=False,
        capture_output=True,
        text=True,
    )
    assert configure.returncode == 0, configure.stderr
    assert (installed / ".paper-mineru.json").is_file()

    show = subprocess.run(
        [sys.executable, "scripts/paper_workflow.py", "configure-mineru", "--show"],
        cwd=installed,
        check=False,
        capture_output=True,
        text=True,
    )
    assert show.returncode == 0, show.stderr
    assert '"standard_token_configured": true' in show.stdout
    assert "test-token" not in show.stdout


def test_single_skill_default_workspace_smoke_test(tmp_path):
    installed = tmp_path / "paper-research-workflow"
    shutil.copytree(SKILL_DIR, installed)
    workspace = tmp_path / "long-term-paper-library"

    setup = subprocess.run(
        [
            sys.executable,
            "scripts/paper_workflow.py",
            "setup",
            "--workspace",
            str(workspace),
            "--save-default",
        ],
        cwd=installed,
        check=False,
        capture_output=True,
        text=True,
    )
    assert setup.returncode == 0, setup.stderr
    assert (installed / ".paper-workspace.json").is_file()
    setup_payload = json.loads(setup.stdout)
    assert setup_payload["default_saved"] is True

    status = subprocess.run(
        [sys.executable, "scripts/paper_workflow.py", "status"],
        cwd=installed,
        check=False,
        capture_output=True,
        text=True,
    )
    assert status.returncode == 0, status.stderr
    assert '"papers": {}' in status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["workspace"] == str(workspace.resolve())
