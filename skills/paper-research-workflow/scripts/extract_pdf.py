from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from shared.scripts.mineru_cloud import (
        MinerUApiError,
        MinerUConfigError,
        default_config_path as default_mineru_config_path,
        load_mineru_config,
        parse_with_agent_cloud,
        parse_with_standard_cloud,
    )
    from shared.scripts.paper_research_common import write_json
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    from mineru_cloud import (
        MinerUApiError,
        MinerUConfigError,
        default_config_path as default_mineru_config_path,
        load_mineru_config,
        parse_with_agent_cloud,
        parse_with_standard_cloud,
    )
    from paper_research_common import write_json


@dataclass(frozen=True)
class ExtractionMetrics:
    chars: int
    pages: int
    table_markers: int
    formula_markers: int


def choose_extraction_strategy(metrics: ExtractionMetrics) -> str:
    if metrics.chars < max(1000, metrics.pages * 400):
        return "mineru"
    if metrics.formula_markers >= 50:
        return "mineru"
    if metrics.table_markers >= 20:
        return "mineru"
    return "lightweight"


def _ensure_companion_files(output_dir: Path) -> None:
    for filename in ["tables.md", "equations.md", "figures.md"]:
        path = output_dir / filename
        if not path.exists():
            path.write_text("", encoding="utf-8")


def _best_markdown_file(mineru_output_dir: Path) -> Path:
    preferred = ["full.md", "output.md", "text.md"]
    for filename in preferred:
        path = mineru_output_dir / filename
        if path.exists():
            return path
    candidates = sorted(mineru_output_dir.rglob("*.md"), key=lambda path: path.stat().st_size, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No Markdown file found under {mineru_output_dir}")
    return candidates[0]


def _measure_text(text: str) -> ExtractionMetrics:
    pages = max(1, text.count("\f") + 1)
    table_markers = text.lower().count("table ") + text.count("|")
    formula_markers = sum(text.count(marker) for marker in ["=", "\\(", "\\[", "$", "∑"])
    return ExtractionMetrics(chars=len(text.strip()), pages=pages, table_markers=table_markers, formula_markers=formula_markers)


def normalize_mineru_outputs(mineru_output_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    best_markdown = _best_markdown_file(mineru_output_dir)
    text = best_markdown.read_text(encoding="utf-8", errors="replace")
    (output_dir / "text.md").write_text(text, encoding="utf-8")
    _ensure_companion_files(output_dir)
    manifest = {
        "status": "ok",
        "strategy": "mineru",
        "source_markdown": str(best_markdown),
        "metrics": _measure_text(text).__dict__,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def default_mineru_wrapper() -> Path:
    return Path(__file__).resolve().with_name("mineru_to_md.sh")


def resolve_mineru_backend(backend: str = "auto") -> str:
    if backend not in {"auto", "custom", "local", "standard-cloud", "agent-cloud"}:
        raise ValueError(f"Unsupported MinerU backend: {backend}")
    if backend != "auto":
        return backend
    if os.environ.get("MINERU_TO_MD", "").strip():
        return "custom"
    if os.environ.get("MINERU_TOKEN", "").strip():
        return "standard-cloud"
    if load_mineru_config(default_mineru_config_path()).standard_token:
        return "standard-cloud"
    if shutil.which("mineru"):
        return "local"
    return "agent-cloud"


def extract_lightweight(pdf_path: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    text = ""
    tool = ""

    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        result = subprocess.run(
            [pdftotext, "-layout", str(pdf_path), "-"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            text = result.stdout
            tool = "pdftotext"

    if not text:
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(str(pdf_path))
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
            tool = "pypdf"
        except Exception as exc:  # pragma: no cover - depends on optional dependency and input
            manifest = {
                "status": "failed",
                "strategy": "lightweight",
                "reason": f"lightweight extraction failed: {exc}",
            }
            write_json(output_dir / "manifest.json", manifest)
            return manifest

    (output_dir / "text.md").write_text(text, encoding="utf-8")
    _ensure_companion_files(output_dir)
    metrics = _measure_text(text)
    manifest = {
        "status": "ok",
        "strategy": "lightweight",
        "tool": tool,
        "metrics": metrics.__dict__,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _failed_mineru_manifest(output_dir: Path, reason: str, backend: str) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "status": "failed",
        "strategy": "mineru",
        "backend": backend,
        "reason": reason,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _run_mineru(pdf_path: Path, output_dir: Path, mineru_wrapper: str, backend: str = "auto") -> dict[str, Any]:
    resolved_backend = resolve_mineru_backend(backend)
    if resolved_backend == "standard-cloud":
        try:
            with tempfile.TemporaryDirectory() as tmp:
                mineru_out = Path(tmp) / "mineru"
                parse_with_standard_cloud(pdf_path.resolve(), mineru_out)
                manifest = normalize_mineru_outputs(mineru_out, output_dir)
                manifest["backend"] = "standard-cloud"
                write_json(output_dir / "manifest.json", manifest)
                return manifest
        except (MinerUApiError, MinerUConfigError) as exc:
            return _failed_mineru_manifest(output_dir, str(exc), "standard-cloud")
    if resolved_backend == "agent-cloud":
        try:
            with tempfile.TemporaryDirectory() as tmp:
                mineru_out = Path(tmp) / "mineru"
                parse_with_agent_cloud(pdf_path.resolve(), mineru_out)
                manifest = normalize_mineru_outputs(mineru_out, output_dir)
                manifest["backend"] = "agent-cloud"
                write_json(output_dir / "manifest.json", manifest)
                return manifest
        except MinerUApiError as exc:
            return _failed_mineru_manifest(output_dir, str(exc), "agent-cloud")

    wrapper = Path(mineru_wrapper)
    if not wrapper.exists():
        return _failed_mineru_manifest(output_dir, f"MinerU wrapper not found: {wrapper}", resolved_backend)

    with tempfile.TemporaryDirectory() as tmp:
        mineru_out = Path(tmp) / "mineru"
        result = subprocess.run(
            [str(wrapper), str(pdf_path.resolve()), "--output", str(mineru_out)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return _failed_mineru_manifest(
                output_dir,
                result.stderr.strip() or result.stdout.strip() or "MinerU wrapper failed",
                resolved_backend,
            )
        manifest = normalize_mineru_outputs(mineru_out, output_dir)
        manifest["backend"] = resolved_backend
        write_json(output_dir / "manifest.json", manifest)
        return manifest


def extract_pdf(
    pdf_path: Path,
    output_dir: Path,
    prefer_mineru: bool = False,
    no_mineru: bool = False,
    mineru_wrapper: str | None = None,
    mineru_backend: str = "auto",
) -> dict[str, Any]:
    if prefer_mineru:
        if no_mineru:
            raise ValueError("prefer_mineru and no_mineru cannot both be true")
        return _run_mineru(
            pdf_path,
            output_dir,
            str(Path(mineru_wrapper) if mineru_wrapper else default_mineru_wrapper()),
            backend=mineru_backend,
        )

    manifest = extract_lightweight(pdf_path, output_dir)
    if no_mineru or manifest.get("status") != "ok":
        return manifest

    metrics = manifest.get("metrics", {})
    strategy = choose_extraction_strategy(ExtractionMetrics(**metrics))
    if strategy == "lightweight":
        return manifest
    return _run_mineru(
        pdf_path,
        output_dir,
        str(Path(mineru_wrapper) if mineru_wrapper else default_mineru_wrapper()),
        backend=mineru_backend,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a local PDF into normalized Markdown artifacts.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefer-mineru", action="store_true")
    parser.add_argument("--no-mineru", action="store_true")
    parser.add_argument(
        "--mineru-wrapper",
        default=None,
    )
    parser.add_argument(
        "--mineru-backend",
        choices=["auto", "custom", "local", "standard-cloud", "agent-cloud"],
        default="auto",
    )
    args = parser.parse_args()

    manifest = extract_pdf(
        args.pdf,
        args.output,
        prefer_mineru=args.prefer_mineru,
        no_mineru=args.no_mineru,
        mineru_wrapper=args.mineru_wrapper,
        mineru_backend=args.mineru_backend,
    )
    print(manifest.get("status", "unknown"))
    return 0 if manifest.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
