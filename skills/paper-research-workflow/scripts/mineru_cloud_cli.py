from __future__ import annotations

import argparse
import json
from pathlib import Path

from mineru_cloud import MinerUApiError, MinerUConfigError, parse_with_agent_cloud, parse_with_standard_cloud


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bundled MinerU cloud extraction.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backend", choices=["auto", "standard-cloud", "agent-cloud"], default="auto")
    args = parser.parse_args()

    backend = args.backend
    if backend == "auto":
        backend = "standard-cloud"
    try:
        if backend == "standard-cloud":
            result = parse_with_standard_cloud(args.pdf, args.output)
        else:
            result = parse_with_agent_cloud(args.pdf, args.output)
    except (MinerUApiError, MinerUConfigError) as exc:
        print(str(exc))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
