from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


def normalize_slug(value: str, max_words: int = 8) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = ascii_value.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    parts = [part for part in slug.split("-") if part]
    return "-".join(parts[:max_words]) or "untitled"


def make_paper_id(title: str, year: int | str | None) -> str:
    year_text = str(year) if year else "unknown-year"
    slug = normalize_slug(title)
    digest = hashlib.sha1(f"{year_text}|{title}".encode("utf-8")).hexdigest()[:6]
    return f"{year_text}-{slug}-{digest}"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
