from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent / "paper-research-workflow" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from paper_research_common import make_paper_id, normalize_slug, read_json, write_json  # noqa: E402
from validate_memory import validate_memory  # noqa: E402
