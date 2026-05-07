from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import shutil
import time
from pathlib import Path
from typing import Any

try:
    from shared.scripts.classify_paper import classify_text, infer_year
    from shared.scripts.extract_pdf import extract_pdf
    from shared.scripts.kb_query import load_memories, rank_related_papers
    from shared.scripts.mineru_cloud import mineru_config_status, save_mineru_config
    from shared.scripts.paper_research_common import make_paper_id, read_json, write_json
    from shared.scripts.validate_memory import validate_memory
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from classify_paper import classify_text, infer_year
    from extract_pdf import extract_pdf
    from kb_query import load_memories, rank_related_papers
    from mineru_cloud import mineru_config_status, save_mineru_config
    from paper_research_common import make_paper_id, read_json, write_json
    from validate_memory import validate_memory


WORKSPACE_DIRS = [
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
]

DEFAULT_WORKSPACE_CONFIG = ".paper-workspace.json"


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[1] / DEFAULT_WORKSPACE_CONFIG


def save_default_workspace(workspace: Path, config_path: Path | None = None) -> Path:
    path = config_path or default_config_path()
    resolved = workspace.expanduser().resolve()
    write_json(path, {"workspace": str(resolved)})
    return resolved


def load_default_workspace(config_path: Path | None = None) -> Path | None:
    path = config_path or default_config_path()
    if not path.exists():
        return None
    data = read_json(path)
    workspace = data.get("workspace") if isinstance(data, dict) else None
    if not workspace:
        return None
    return Path(workspace).expanduser().resolve()


def resolve_workspace(workspace: Path | None, config_path: Path | None = None) -> Path:
    if workspace is not None:
        return workspace.expanduser().resolve()
    configured = load_default_workspace(config_path)
    if configured is not None:
        return configured
    raise SystemExit(
        "No workspace configured. Run: python scripts/paper_workflow.py setup "
        "--workspace /path/to/paper-library --save-default"
    )


def setup_workspace(workspace: Path) -> None:
    for relative in WORKSPACE_DIRS:
        (workspace / relative).mkdir(parents=True, exist_ok=True)
    state_path = workspace / "state/papers.json"
    if not state_path.exists():
        write_json(state_path, {"papers": {}})


def load_state(workspace: Path) -> dict[str, Any]:
    state_path = workspace / "state/papers.json"
    if not state_path.exists():
        return {"papers": {}}
    state = read_json(state_path)
    if not isinstance(state, dict) or "papers" not in state:
        return {"papers": {}}
    return state


def update_state(workspace: Path, paper_id: str, stage: str, payload: dict[str, Any]) -> None:
    setup_workspace(workspace)
    state = load_state(workspace)
    paper_state = state.setdefault("papers", {}).setdefault(paper_id, {"stages": {}})
    paper_state.setdefault("stages", {})[stage] = payload
    write_json(workspace / "state/papers.json", state)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _suite_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    if (script_dir.parent / "templates").is_dir() and (script_dir.parent / "schemas").is_dir():
        return script_dir.parent
    return _repo_root() / "shared"


def _local_mineru_script() -> Path:
    return Path(__file__).resolve().with_name("mineru_local_docker.sh")


def _web_dir() -> Path:
    return _suite_root() / "web"


def web_service_state_path() -> Path:
    return _suite_root() / ".paper-web-service.json"


def web_service_log_path() -> Path:
    return _suite_root() / ".paper-web-service.log"


def _template_memory() -> dict[str, Any]:
    return read_json(_suite_root() / "templates/paper-memory.json")


def _archive_pdf(pdf_path: Path, workspace: Path, paper_id: str, classification: dict[str, Any], year: int | None) -> Path:
    primary_domain = (classification.get("domains") or ["computer-science"])[0]
    archived = workspace / "papers/by-domain" / primary_domain / f"{paper_id}.pdf"
    archived.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf_path, archived)
    if year:
        year_dir = workspace / "papers/by-year" / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        year_link = year_dir / f"{paper_id}.pdf"
        if not year_link.exists():
            shutil.copy2(pdf_path, year_link)
    return archived


def ingest_pdf(
    workspace: Path,
    pdf_path: Path,
    prefer_mineru: bool = False,
    no_mineru: bool = False,
    mineru_backend: str = "auto",
) -> dict[str, Any]:
    setup_workspace(workspace)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    scratch = workspace / "extracted/_incoming"
    manifest = extract_pdf(
        pdf_path,
        scratch,
        prefer_mineru=prefer_mineru,
        no_mineru=no_mineru,
        mineru_backend=mineru_backend,
    )
    text_path = scratch / "text.md"
    text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.exists() else ""
    year = infer_year(text)
    title = pdf_path.stem.replace("_", " ").replace("-", " ").strip() or "Untitled Paper"
    paper_id = make_paper_id(title, year)
    extracted_dir = workspace / "extracted" / paper_id
    if extracted_dir.exists():
        shutil.rmtree(extracted_dir)
    scratch.rename(extracted_dir)

    classification = classify_text(text)
    archived = _archive_pdf(pdf_path, workspace, paper_id, classification, year)
    memory = _template_memory()
    memory.update(
        {
            "paper_id": paper_id,
            "title": title,
            "year": year,
            "source": {
                **memory["source"],
                "input_path": str(pdf_path),
                "archived_path": str(archived),
            },
            "classification": classification,
        }
    )
    memory["status"]["ingested"] = True
    memory_path = workspace / "knowledge/papers" / f"{paper_id}.json"
    write_json(memory_path, memory)
    update_state(
        workspace,
        paper_id,
        "ingested",
        {
            "input_path": str(pdf_path),
            "memory_path": str(memory_path),
            "extracted_dir": str(extracted_dir),
            "manifest_status": manifest.get("status"),
        },
    )
    return {"paper_id": paper_id, "memory_path": str(memory_path), "manifest": manifest}


def validate_workspace(workspace: Path) -> dict[str, list[str]]:
    schema = _suite_root() / "schemas/paper-memory.schema.json"
    results: dict[str, list[str]] = {}
    for memory_path in sorted((workspace / "knowledge/papers").glob("*.json")):
        results[memory_path.name] = validate_memory(read_json(memory_path), schema)
    return results


def query_workspace(workspace: Path, paper_id: str, limit: int = 10) -> list[dict[str, Any]]:
    memories = load_memories(workspace / "knowledge/papers")
    target = next((memory for memory in memories if memory.get("paper_id") == paper_id), None)
    if target is None:
        raise KeyError(paper_id)
    return rank_related_papers(target, memories, limit)


def local_mineru_status() -> dict[str, Any]:
    script = _local_mineru_script()
    if not script.exists():
        return {"available": False, "reason": f"missing script: {script}"}

    result = subprocess.run(
        [str(script), "status"],
        check=False,
        capture_output=True,
        text=True,
    )
    payload: dict[str, Any]
    try:
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw_stdout": result.stdout.strip()}
    payload["available"] = result.returncode == 0
    if result.stderr.strip():
        payload["stderr"] = result.stderr.strip()
    return payload


def enable_local_mineru(
    docker_dir: Path | None = None,
    dockerfile_url: str | None = None,
    source_archive_url: str | None = None,
    source_subdir: str | None = None,
    image: str | None = None,
) -> dict[str, Any]:
    script = _local_mineru_script()
    if not script.exists():
        raise FileNotFoundError(script)

    command = [str(script), "enable"]
    if docker_dir is not None:
        command.extend(["--docker-dir", str(docker_dir)])
    if dockerfile_url:
        command.extend(["--dockerfile-url", dockerfile_url])
    if source_archive_url:
        command.extend(["--source-archive-url", source_archive_url])
    if source_subdir:
        command.extend(["--source-subdir", source_subdir])
    if image:
        command.extend(["--image", image])

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    payload = {
        "ok": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "command": " ".join(command),
    }
    return payload


def _process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def web_workbench_status() -> dict[str, Any]:
    state_path = web_service_state_path()
    if not state_path.exists():
        return {
            "running": False,
            "state_path": str(state_path),
            "log_path": str(web_service_log_path()),
        }
    state = read_json(state_path)
    pid = int(state.get("pid", 0))
    running = bool(pid and _process_running(pid))
    return {
        **state,
        "running": running,
        "state_path": str(state_path),
        "log_path": str(web_service_log_path()),
    }


def _start_web_workbench(port: int = 5173, host: str = "127.0.0.1") -> dict[str, Any]:
    status = web_workbench_status()
    if status.get("running"):
        return {"ok": True, **status}

    web_dir = _web_dir()
    if not (web_dir / "package.json").exists():
        return {"ok": False, "reason": f"missing web package: {web_dir / 'package.json'}"}

    log_path = web_service_log_path()
    log_file = log_path.open("a", encoding="utf-8")
    command = ["npm", "run", "dev", "--", "--host", host, "--port", str(port)]
    process = subprocess.Popen(
        command,
        cwd=web_dir,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )
    url = f"http://{host}:{port}"
    state = {
        "pid": process.pid,
        "url": url,
        "host": host,
        "port": port,
        "command": " ".join(command),
        "web_dir": str(web_dir),
        "started_at": int(time.time()),
    }
    write_json(web_service_state_path(), state)
    return {"ok": True, "running": True, **state, "log_path": str(log_path)}


def _stop_web_workbench() -> dict[str, Any]:
    status = web_workbench_status()
    state_path = web_service_state_path()
    pid = int(status.get("pid", 0) or 0)
    if status.get("running") and pid:
        os.kill(pid, signal.SIGTERM)
    if state_path.exists():
        state_path.unlink()
    return {
        "ok": True,
        "running": False,
        "stopped_pid": pid or None,
        "state_path": str(state_path),
    }


def _web_workbench_logs(lines: int = 80) -> dict[str, Any]:
    log_path = web_service_log_path()
    if not log_path.exists():
        return {"ok": True, "log_path": str(log_path), "lines": []}
    content = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"ok": True, "log_path": str(log_path), "lines": content[-lines:]}


def run_web_workbench(
    command: str = "dev",
    port: int = 5173,
    host: str = "127.0.0.1",
    log_lines: int = 80,
) -> dict[str, Any]:
    if command == "start":
        return _start_web_workbench(port=port, host=host)
    if command == "status":
        return {"ok": True, **web_workbench_status()}
    if command == "stop":
        return _stop_web_workbench()
    if command == "logs":
        return _web_workbench_logs(log_lines)

    web_dir = _web_dir()
    if not (web_dir / "package.json").exists():
        return {"ok": False, "reason": f"missing web package: {web_dir / 'package.json'}"}
    result = subprocess.run(
        ["npm", "run", command],
        check=False,
        cwd=web_dir,
    )
    return {"ok": result.returncode == 0, "command": f"npm run {command}", "web_dir": str(web_dir)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper research workflow helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup")
    setup_parser.add_argument("--workspace", type=Path, required=True)
    setup_parser.add_argument("--save-default", action="store_true")

    mineru_parser = subparsers.add_parser("configure-mineru")
    mineru_parser.add_argument("--standard-token", default=None)
    mineru_parser.add_argument("--show", action="store_true")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--workspace", type=Path, default=None)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--workspace", type=Path, default=None)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--workspace", type=Path, default=None)
    query_parser.add_argument("--paper-id", required=True)
    query_parser.add_argument("--limit", type=int, default=10)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("pdf", type=Path)
    ingest_parser.add_argument("--workspace", type=Path, default=None)
    ingest_parser.add_argument("--prefer-mineru", action="store_true")
    ingest_parser.add_argument("--no-mineru", action="store_true")
    ingest_parser.add_argument(
        "--mineru-backend",
        choices=["auto", "local", "standard-cloud", "agent-cloud"],
        default="auto",
    )

    local_mineru_parser = subparsers.add_parser("local-mineru")
    local_mineru_parser.add_argument("--status", action="store_true")
    local_mineru_parser.add_argument("--enable", action="store_true")
    local_mineru_parser.add_argument("--docker-dir", type=Path, default=None)
    local_mineru_parser.add_argument("--dockerfile-url", default=None)
    local_mineru_parser.add_argument("--source-archive-url", default=None)
    local_mineru_parser.add_argument("--source-subdir", default=None)
    local_mineru_parser.add_argument("--image", default=None)

    web_parser = subparsers.add_parser("web")
    web_parser.add_argument(
        "--web-command",
        choices=["dev", "build", "test", "preview", "start", "status", "stop", "logs"],
        default="dev",
    )
    web_parser.add_argument("--port", type=int, default=5173)
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--log-lines", type=int, default=80)

    args = parser.parse_args()

    if args.command == "setup":
        workspace = resolve_workspace(args.workspace)
        setup_workspace(workspace)
        if args.save_default:
            save_default_workspace(workspace)
        print(workspace)
        return 0
    if args.command == "configure-mineru":
        if args.standard_token:
            save_mineru_config(args.standard_token)
        print(json.dumps(mineru_config_status(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "status":
        print(json.dumps(load_state(resolve_workspace(args.workspace)), ensure_ascii=False, indent=2))
        return 0
    if args.command == "validate":
        results = validate_workspace(resolve_workspace(args.workspace))
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0 if all(not errors for errors in results.values()) else 1
    if args.command == "query":
        print(
            json.dumps(
                query_workspace(resolve_workspace(args.workspace), args.paper_id, args.limit),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "ingest":
        print(
            json.dumps(
                ingest_pdf(
                    resolve_workspace(args.workspace),
                    args.pdf,
                    prefer_mineru=args.prefer_mineru,
                    no_mineru=args.no_mineru,
                    mineru_backend=args.mineru_backend,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "local-mineru":
        if args.enable:
            result = enable_local_mineru(
                docker_dir=args.docker_dir,
                dockerfile_url=args.dockerfile_url,
                source_archive_url=args.source_archive_url,
                source_subdir=args.source_subdir,
                image=args.image,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["ok"] else 1
        print(json.dumps(local_mineru_status(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "web":
        result = run_web_workbench(
            args.web_command,
            port=args.port,
            host=args.host,
            log_lines=args.log_lines,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
