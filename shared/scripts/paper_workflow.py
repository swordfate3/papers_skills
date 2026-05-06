from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

try:
    from shared.scripts.classify_paper import classify_text, infer_year
    from shared.scripts.extract_pdf import extract_pdf
    from shared.scripts.kb_query import load_memories, rank_related_papers
    from shared.scripts.paper_research_common import make_paper_id, read_json, write_json
    from shared.scripts.validate_memory import validate_memory
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from classify_paper import classify_text, infer_year
    from extract_pdf import extract_pdf
    from kb_query import load_memories, rank_related_papers
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


def _template_memory() -> dict[str, Any]:
    return read_json(_repo_root() / "shared/templates/paper-memory.json")


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


def ingest_pdf(workspace: Path, pdf_path: Path, prefer_mineru: bool = False, no_mineru: bool = False) -> dict[str, Any]:
    setup_workspace(workspace)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    scratch = workspace / "extracted/_incoming"
    manifest = extract_pdf(pdf_path, scratch, prefer_mineru=prefer_mineru, no_mineru=no_mineru)
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
    schema = _repo_root() / "shared/schemas/paper-memory.schema.json"
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper research workflow helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup")
    setup_parser.add_argument("--workspace", type=Path, default=Path("workspace"))

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--workspace", type=Path, default=Path("workspace"))

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--workspace", type=Path, default=Path("workspace"))

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--workspace", type=Path, default=Path("workspace"))
    query_parser.add_argument("--paper-id", required=True)
    query_parser.add_argument("--limit", type=int, default=10)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("pdf", type=Path)
    ingest_parser.add_argument("--workspace", type=Path, default=Path("workspace"))
    ingest_parser.add_argument("--prefer-mineru", action="store_true")
    ingest_parser.add_argument("--no-mineru", action="store_true")

    args = parser.parse_args()

    if args.command == "setup":
        setup_workspace(args.workspace)
        print(args.workspace)
        return 0
    if args.command == "status":
        print(json.dumps(load_state(args.workspace), ensure_ascii=False, indent=2))
        return 0
    if args.command == "validate":
        results = validate_workspace(args.workspace)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0 if all(not errors for errors in results.values()) else 1
    if args.command == "query":
        print(json.dumps(query_workspace(args.workspace, args.paper_id, args.limit), ensure_ascii=False, indent=2))
        return 0
    if args.command == "ingest":
        print(
            json.dumps(
                ingest_pdf(args.workspace, args.pdf, prefer_mineru=args.prefer_mineru, no_mineru=args.no_mineru),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
