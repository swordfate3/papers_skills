from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from shared.scripts.paper_research_common import read_json
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from paper_research_common import read_json


FIELD_PATHS = {
    "domains": ("classification", "domains"),
    "tasks": ("classification", "tasks"),
    "keywords": ("classification", "keywords"),
    "datasets": ("evidence", "datasets"),
    "metrics": ("evidence", "metrics"),
    "limitations": ("critique", "limitations"),
}

WEIGHTS = {
    "domains": 3,
    "tasks": 4,
    "keywords": 2,
    "datasets": 3,
    "metrics": 2,
    "limitations": 1,
}


def _values(memory: dict[str, Any], path: tuple[str, str]) -> set[str]:
    value = memory.get(path[0], {}).get(path[1], [])
    if not isinstance(value, list):
        return set()
    return {str(item).lower() for item in value}


def load_memories(kb_dir: Path) -> list[dict[str, Any]]:
    memories: list[dict[str, Any]] = []
    for path in sorted(kb_dir.glob("*.json")):
        memory = read_json(path)
        if isinstance(memory, dict):
            memories.append(memory)
    return memories


def rank_related_papers(
    target: dict[str, Any],
    candidates: list[dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    target_id = target.get("paper_id")
    for candidate in candidates:
        if candidate.get("paper_id") == target_id:
            continue
        score = 0
        matched_fields: dict[str, list[str]] = {}
        for field, path in FIELD_PATHS.items():
            matches = sorted(_values(target, path) & _values(candidate, path))
            if matches:
                score += len(matches) * WEIGHTS[field]
                matched_fields[field] = matches
        ranked.append(
            {
                "paper_id": candidate.get("paper_id", ""),
                "title": candidate.get("title", ""),
                "score": score,
                "matched_fields": matched_fields,
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["paper_id"]))
    return ranked[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Query related papers from a file knowledge base.")
    parser.add_argument("--kb", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    memories = load_memories(args.kb)
    target = next((memory for memory in memories if memory.get("paper_id") == args.paper_id), None)
    if target is None:
        print(f"paper_id not found: {args.paper_id}")
        return 1
    print(json.dumps(rank_related_papers(target, memories, args.limit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
