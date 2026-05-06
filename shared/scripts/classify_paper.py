from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


VENUES = [
    "NeurIPS",
    "ICML",
    "ICLR",
    "CVPR",
    "ACL",
    "SIGCOMM",
    "SOSP",
    "OSDI",
    "USENIX",
    "IEEE S&P",
    "CCS",
    "NDSS",
]

DOMAIN_KEYWORDS = {
    "machine-learning": [
        "ablation",
        "accuracy",
        "baseline",
        "checkpoint",
        "dataset",
        "imagenet",
        "learning",
        "model",
        "neural network",
        "transformer",
        "train",
    ],
    "systems": [
        "cluster",
        "distributed",
        "latency",
        "scheduler",
        "storage",
        "throughput",
    ],
    "security": [
        "attack",
        "fuzzing",
        "malware",
        "privacy",
        "secure",
        "security",
        "side channel",
        "symbolic execution",
        "vulnerability",
    ],
    "software-engineering": [
        "bug",
        "code generation",
        "debug",
        "program analysis",
        "repository",
        "software",
        "static analysis",
        "test",
    ],
    "databases": [
        "database",
        "index",
        "join",
        "query",
        "sql",
        "transaction",
    ],
    "data-mining": [
        "clustering",
        "graph mining",
        "mining",
        "recommendation",
    ],
    "robotics": [
        "control",
        "manipulation",
        "navigation",
        "planning",
        "robot",
    ],
}

KEYWORDS = [
    "ablation",
    "accuracy",
    "baseline",
    "classification",
    "dataset",
    "distributed",
    "fuzzing",
    "imagenet",
    "latency",
    "scheduler",
    "symbolic-execution",
    "throughput",
    "transformer",
]


def infer_year(text: str) -> int | None:
    current_limit = date.today().year + 1
    matches = [(match.group(), match.start()) for match in re.finditer(r"\b(19[9]\d|20\d{2})\b", text)]
    years = [(int(year), position) for year, position in matches if 1990 <= int(year) <= current_limit]
    if not years:
        return None

    lowered = text.lower()
    venue_positions = [lowered.find(venue.lower()) for venue in VENUES if venue.lower() in lowered]
    venue_positions = [position for position in venue_positions if position >= 0]
    if venue_positions:
        return min(years, key=lambda item: min(abs(item[1] - venue_pos) for venue_pos in venue_positions))[0]
    return max(year for year, _ in years)


def _count_matches(text: str, phrases: list[str]) -> int:
    return sum(1 for phrase in phrases if phrase in text)


def classify_text(text: str) -> dict[str, list[str] | str]:
    lowered = text.lower().replace("_", "-")
    domain_scores = {
        domain: _count_matches(lowered, [keyword.lower() for keyword in keywords])
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    domains = [domain for domain, score in sorted(domain_scores.items(), key=lambda item: (-item[1], item[0])) if score]
    if not domains:
        domains = ["computer-science"]

    keywords: list[str] = []
    for keyword in KEYWORDS:
        normalized = keyword.replace("-", " ")
        if keyword in lowered or normalized in lowered:
            keywords.append(keyword)

    tasks: list[str] = []
    for task in ["classification", "generation", "detection", "scheduling", "query-optimization", "fuzzing"]:
        if task.replace("-", " ") in lowered or task in lowered:
            tasks.append(task)

    paper_type = "empirical"
    if any(term in lowered for term in ["benchmark", "dataset"]):
        paper_type = "benchmark"
    if any(term in lowered for term in ["survey", "taxonomy"]):
        paper_type = "survey"
    if any(term in lowered for term in ["system", "framework", "platform"]):
        paper_type = "system"

    return {
        "domains": domains,
        "paper_type": paper_type,
        "tasks": tasks,
        "keywords": keywords,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify extracted paper text.")
    parser.add_argument("text_file", type=Path)
    args = parser.parse_args()
    text = args.text_file.read_text(encoding="utf-8", errors="replace")
    result = classify_text(text)
    result["year"] = infer_year(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
