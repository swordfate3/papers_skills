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
        "scripts/mineru_to_md.sh",
        "schemas/paper-memory.schema.json",
        "templates/paper-memory.json",
        "references/pdf-processing.md",
        "references/mineru-local.md",
        "references/child-skills/paper-ingest-classifier.md",
        "references/child-skills/paper-innovation-miner.md",
    ]:
        assert (SKILL_DIR / relative).is_file()


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

    status = subprocess.run(
        [sys.executable, "scripts/paper_workflow.py", "status", "--workspace", str(workspace)],
        cwd=installed,
        check=False,
        capture_output=True,
        text=True,
    )
    assert status.returncode == 0, status.stderr
    assert '"papers": {}' in status.stdout
