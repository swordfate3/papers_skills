# Paper Research Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved semi-automated paper-reading skill suite with seven skills, shared schemas, templates, deterministic helper scripts, and tests.

**Architecture:** The repository will contain seven skill folders under `skills/` and shared reusable resources under `shared/`. Skills stay concise and procedural; scripts handle deterministic workspace setup, PDF extraction routing, paper IDs, classification heuristics, knowledge-base querying, and schema validation. The first version uses a file-based knowledge base and local PDF input only.

**Tech Stack:** Markdown skills, YAML frontmatter, Python 3 standard library, `pytest`, JSON Schema draft-style validation implemented with a small local validator or optional `jsonschema` fallback, Poppler `pdftotext` when available, optional MinerU wrapper integration.

---

## File Map

- Create `skills/paper-research-workflow/SKILL.md`: orchestration skill.
- Create `skills/paper-ingest-classifier/SKILL.md`: PDF extraction, classification, and archive skill.
- Create `skills/paper-plain-explainer/SKILL.md`: beginner explanation skill.
- Create `skills/paper-expert-reader/SKILL.md`: expert reading skill.
- Create `skills/paper-code-reproducer/SKILL.md`: reproduction planning skill.
- Create `skills/paper-knowledge-base/SKILL.md`: file knowledge-base write/update/validate skill.
- Create `skills/paper-innovation-miner/SKILL.md`: related-paper retrieval and innovation mining skill.
- Create `skills/*/agents/openai.yaml`: UI metadata for each skill.
- Create `shared/templates/*.json|*.md`: canonical output templates.
- Create `shared/schemas/*.schema.json`: schema files for paper memory, paper card metadata, reproduction plan metadata, and innovation brief metadata.
- Create `shared/scripts/paper_research_common.py`: shared filesystem, JSON, slug, hash, and memory helpers.
- Create `shared/scripts/validate_memory.py`: validate paper memory files against schema.
- Create `shared/scripts/extract_pdf.py`: lightweight extraction, extraction metrics, and portable MinerU fallback routing.
- Create `shared/scripts/classify_paper.py`: metadata and domain classification heuristics.
- Create `shared/scripts/kb_query.py`: file-based knowledge-base search.
- Create `shared/scripts/paper_workflow.py`: unified CLI for setup, ingest, validate, query, and status.
- Create `tests/`: focused pytest coverage for schemas, templates, helper functions, extraction fallback, classification, KB query, and workflow state.

## Task 1: Project Test Harness and Skill Initialization Helpers

**Files:**
- Create: `pyproject.toml`
- Create: `tests/test_repo_structure.py`
- Create: `skills/.gitkeep`
- Create: `shared/scripts/.gitkeep`
- Create: `shared/schemas/.gitkeep`
- Create: `shared/templates/.gitkeep`

- [ ] **Step 1: Create minimal Python project metadata**

Add `pyproject.toml`:

```toml
[project]
name = "paper-research-skills"
version = "0.1.0"
description = "Semi-automated paper reading skill suite"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 2: Create expected top-level directories**

Run:

```bash
mkdir -p skills shared/scripts shared/schemas shared/templates tests
touch skills/.gitkeep shared/scripts/.gitkeep shared/schemas/.gitkeep shared/templates/.gitkeep
```

- [ ] **Step 3: Write the failing repository structure test**

Add `tests/test_repo_structure.py`:

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_expected_top_level_directories_exist():
    for relative in ["skills", "shared/scripts", "shared/schemas", "shared/templates"]:
        assert (ROOT / relative).is_dir()


def test_expected_skill_names_are_reserved():
    expected = {
        "paper-research-workflow",
        "paper-ingest-classifier",
        "paper-plain-explainer",
        "paper-expert-reader",
        "paper-code-reproducer",
        "paper-knowledge-base",
        "paper-innovation-miner",
    }
    actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
    assert expected <= actual
```

- [ ] **Step 4: Run the test and observe the skill-folder failure**

Run:

```bash
uv run pytest tests/test_repo_structure.py -q
```

Expected: the first test passes and the second test fails because the seven skill folders do not exist yet.

- [ ] **Step 5: Commit the harness**

Run:

```bash
git add pyproject.toml tests/test_repo_structure.py skills/.gitkeep shared/scripts/.gitkeep shared/schemas/.gitkeep shared/templates/.gitkeep
git commit -m "chore: 初始化论文技能包测试骨架"
```

## Task 2: Create Seven Skill Folders

**Files:**
- Create: `skills/<skill-name>/SKILL.md`
- Create: `skills/<skill-name>/agents/openai.yaml`
- Modify: `tests/test_repo_structure.py`

- [ ] **Step 1: Initialize skill folders with the official generator**

Run the generator once per skill:

```bash
python /home/fate/.codex/skills/.system/skill-creator/scripts/init_skill.py paper-research-workflow --path skills --interface display_name="Paper Research Workflow" --interface short_description="Orchestrate paper reading workflows" --interface default_prompt="Use $paper-research-workflow to read a local paper through the full research workflow."
python /home/fate/.codex/skills/.system/skill-creator/scripts/init_skill.py paper-ingest-classifier --path skills --interface display_name="Paper Ingest Classifier" --interface short_description="Extract, classify, and archive PDFs" --interface default_prompt="Use $paper-ingest-classifier to ingest and classify a local research PDF."
python /home/fate/.codex/skills/.system/skill-creator/scripts/init_skill.py paper-plain-explainer --path skills --interface display_name="Paper Plain Explainer" --interface short_description="Explain papers in plain language" --interface default_prompt="Use $paper-plain-explainer to explain this paper clearly for a beginner."
python /home/fate/.codex/skills/.system/skill-creator/scripts/init_skill.py paper-expert-reader --path skills --interface display_name="Paper Expert Reader" --interface short_description="Deep expert reading for research papers" --interface default_prompt="Use $paper-expert-reader to analyze this paper like a domain expert."
python /home/fate/.codex/skills/.system/skill-creator/scripts/init_skill.py paper-code-reproducer --path skills --interface display_name="Paper Code Reproducer" --interface short_description="Plan paper code reproduction" --interface default_prompt="Use $paper-code-reproducer to create a reproduction plan for this paper."
python /home/fate/.codex/skills/.system/skill-creator/scripts/init_skill.py paper-knowledge-base --path skills --interface display_name="Paper Knowledge Base" --interface short_description="Maintain paper memory files" --interface default_prompt="Use $paper-knowledge-base to write and validate this paper in the file knowledge base."
python /home/fate/.codex/skills/.system/skill-creator/scripts/init_skill.py paper-innovation-miner --path skills --interface display_name="Paper Innovation Miner" --interface short_description="Mine paper memories for new ideas" --interface default_prompt="Use $paper-innovation-miner to find related papers and propose innovation directions."
```

- [ ] **Step 2: Run repository structure test**

Run:

```bash
uv run pytest tests/test_repo_structure.py -q
```

Expected: PASS.

- [ ] **Step 3: Add skill metadata validation test**

Append to `tests/test_repo_structure.py`:

```python
import re


def test_skill_frontmatter_has_name_and_description():
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert re.search(r"^name: " + re.escape(skill_dir.name) + r"$", text, re.MULTILINE)
        assert re.search(r"^description: .{40,}$", text, re.MULTILINE)
```

- [ ] **Step 4: Run metadata test**

Run:

```bash
uv run pytest tests/test_repo_structure.py -q
```

Expected: PASS after generated descriptions are present. If a generated description is too short, edit that skill's frontmatter description to match its actual trigger context.

- [ ] **Step 5: Commit skill folders**

Run:

```bash
git add skills tests/test_repo_structure.py
git commit -m "feat(skills): 初始化论文研究技能目录"
```

## Task 3: Shared Schemas and Templates

**Files:**
- Create: `shared/schemas/paper-memory.schema.json`
- Create: `shared/schemas/paper-card.schema.json`
- Create: `shared/schemas/reproduction-plan.schema.json`
- Create: `shared/schemas/innovation-brief.schema.json`
- Create: `shared/templates/paper-memory.json`
- Create: `shared/templates/paper-card.md`
- Create: `shared/templates/expert-reading.md`
- Create: `shared/templates/reproduction-plan.md`
- Create: `shared/templates/innovation-brief.md`
- Create: `tests/test_templates_and_schemas.py`

- [ ] **Step 1: Write failing schema/template tests**

Add `tests/test_templates_and_schemas.py`:

```python
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_paper_memory_schema_requires_core_fields():
    schema = load_json("shared/schemas/paper-memory.schema.json")
    assert schema["type"] == "object"
    for field in ["paper_id", "title", "authors", "year", "source", "classification", "core", "evidence", "critique", "reproduction", "innovation", "artifacts", "status"]:
        assert field in schema["required"]


def test_paper_memory_template_matches_required_shape():
    template = load_json("shared/templates/paper-memory.json")
    for field in ["paper_id", "title", "authors", "year", "source", "classification", "core", "evidence", "critique", "reproduction", "innovation", "artifacts", "status"]:
        assert field in template
    assert template["reproduction"]["difficulty"] == "unknown"
    assert template["status"]["kb_validated"] is False


def test_markdown_templates_have_frontmatter_and_required_sections():
    required = {
        "paper-card.md": ["一句话总结", "核心问题", "方法", "证据", "局限性", "术语对照"],
        "expert-reading.md": ["专家结论", "技术机制", "证据质量", "局限与失败模式", "创新启发"],
        "reproduction-plan.md": ["复现目标", "最小可行复现", "依赖与数据", "实验与指标", "风险"],
        "innovation-brief.md": ["来源论文", "创新假设", "最小实验", "风险与证伪"],
    }
    for filename, sections in required.items():
        text = (ROOT / "shared/templates" / filename).read_text(encoding="utf-8")
        assert text.startswith("---\n")
        for section in sections:
            assert f"## {section}" in text
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv run pytest tests/test_templates_and_schemas.py -q
```

Expected: FAIL because schema and template files do not exist.

- [ ] **Step 3: Add `paper-memory.schema.json`**

Create `shared/schemas/paper-memory.schema.json` with the exact top-level fields from the approved spec. Use JSON Schema-compatible keywords: `type`, `required`, `properties`, `items`, `enum`, and `additionalProperties`. Require all top-level fields and require the nested fields shown in the spec for `source`, `classification`, `core`, `evidence`, `critique`, `reproduction`, `innovation`, `artifacts`, and `status`.

- [ ] **Step 4: Add metadata schemas**

Create the three smaller schemas:

```json
{
  "type": "object",
  "required": ["title", "type", "status", "source_papers"],
  "properties": {
    "title": {"type": "string"},
    "type": {"type": "string"},
    "status": {"type": "string"},
    "source_papers": {"type": "array", "items": {"type": "string"}}
  },
  "additionalProperties": true
}
```

Use this shape for `paper-card.schema.json`, `reproduction-plan.schema.json`, and `innovation-brief.schema.json`, changing the allowed `type` enum respectively to `paper_card`, `prototype`, and `note`.

- [ ] **Step 5: Add JSON and Markdown templates**

Create `shared/templates/paper-memory.json` matching the spec's example object and empty/default values.

Create Markdown templates with YAML frontmatter:

```markdown
---
title: ""
type: paper_card
status: pending
source_papers: []
---

## 一句话总结

## 核心问题

## 方法

## 证据

## 局限性

## 术语对照
```

Use analogous frontmatter and required sections for the expert reading, reproduction plan, and innovation brief templates.

- [ ] **Step 6: Run tests**

Run:

```bash
uv run pytest tests/test_templates_and_schemas.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit schemas and templates**

Run:

```bash
git add shared/schemas shared/templates tests/test_templates_and_schemas.py
git commit -m "feat(schema): 添加论文知识库模板和契约"
```

## Task 4: Common Helpers and Memory Validation

**Files:**
- Create: `shared/scripts/paper_research_common.py`
- Create: `shared/scripts/validate_memory.py`
- Create: `tests/test_memory_validation.py`

- [ ] **Step 1: Write failing helper and validator tests**

Add `tests/test_memory_validation.py`:

```python
import json
from pathlib import Path

import pytest

from shared.scripts.paper_research_common import make_paper_id, normalize_slug, read_json, write_json
from shared.scripts.validate_memory import validate_memory


ROOT = Path(__file__).resolve().parents[1]


def test_normalize_slug_is_ascii_stable():
    assert normalize_slug("Attention Is All You Need!") == "attention-is-all-you-need"
    assert normalize_slug("  A/B: Test_of Systems  ") == "a-b-test-of-systems"


def test_make_paper_id_is_stable_and_short():
    first = make_paper_id("Attention Is All You Need", 2017)
    second = make_paper_id("Attention Is All You Need", 2017)
    assert first == second
    assert first.startswith("2017-attention-is-all-you-need-")
    assert len(first.rsplit("-", 1)[-1]) == 6


def test_read_write_json_round_trip(tmp_path):
    path = tmp_path / "nested" / "data.json"
    write_json(path, {"a": 1})
    assert read_json(path) == {"a": 1}


def test_validate_memory_accepts_template():
    memory = json.loads((ROOT / "shared/templates/paper-memory.json").read_text(encoding="utf-8"))
    errors = validate_memory(memory, ROOT / "shared/schemas/paper-memory.schema.json")
    assert errors == []


def test_validate_memory_reports_missing_required_field():
    memory = json.loads((ROOT / "shared/templates/paper-memory.json").read_text(encoding="utf-8"))
    del memory["paper_id"]
    errors = validate_memory(memory, ROOT / "shared/schemas/paper-memory.schema.json")
    assert any("paper_id" in error for error in errors)
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv run pytest tests/test_memory_validation.py -q
```

Expected: FAIL because helper modules do not exist.

- [ ] **Step 3: Implement common helpers**

Create `shared/scripts/paper_research_common.py` with:

```python
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
```

- [ ] **Step 4: Implement memory validation**

Create `shared/scripts/validate_memory.py` with `validate_memory(data: dict, schema_path: Path) -> list[str]`. Implement support for the schema keywords used in this project: `type`, `required`, `properties`, `items`, `enum`, and nested objects/arrays. Also provide a CLI:

```bash
python shared/scripts/validate_memory.py workspace/knowledge/papers/example.json
```

The CLI should print `valid` and exit `0` for valid files, print one error per line and exit `1` for invalid files.

- [ ] **Step 5: Run tests**

Run:

```bash
uv run pytest tests/test_memory_validation.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit helpers**

Run:

```bash
git add shared/scripts/paper_research_common.py shared/scripts/validate_memory.py tests/test_memory_validation.py
git commit -m "feat(validation): 添加论文记忆校验工具"
```

## Task 5: PDF Extraction Routing

**Files:**
- Create: `shared/scripts/extract_pdf.py`
- Create: `tests/test_extract_pdf.py`

- [ ] **Step 1: Write failing extraction routing tests**

Add `tests/test_extract_pdf.py`:

```python
from pathlib import Path

from shared.scripts.extract_pdf import ExtractionMetrics, choose_extraction_strategy, normalize_mineru_outputs


def test_choose_lightweight_for_good_text_pdf():
    metrics = ExtractionMetrics(chars=20000, pages=8, table_markers=2, formula_markers=3)
    assert choose_extraction_strategy(metrics) == "lightweight"


def test_choose_mineru_for_too_little_text():
    metrics = ExtractionMetrics(chars=100, pages=10, table_markers=0, formula_markers=0)
    assert choose_extraction_strategy(metrics) == "mineru"


def test_choose_mineru_for_formula_heavy_pdf():
    metrics = ExtractionMetrics(chars=12000, pages=6, table_markers=1, formula_markers=80)
    assert choose_extraction_strategy(metrics) == "mineru"


def test_normalize_mineru_outputs_picks_markdown_file(tmp_path):
    mineru_dir = tmp_path / "mineru"
    mineru_dir.mkdir()
    (mineru_dir / "full.md").write_text("# Paper\n\ncontent", encoding="utf-8")
    output_dir = tmp_path / "out"
    manifest = normalize_mineru_outputs(mineru_dir, output_dir)
    assert (output_dir / "text.md").read_text(encoding="utf-8").startswith("# Paper")
    assert manifest["strategy"] == "mineru"
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv run pytest tests/test_extract_pdf.py -q
```

Expected: FAIL because `extract_pdf.py` does not exist.

- [ ] **Step 3: Implement extraction routing module**

Create `shared/scripts/extract_pdf.py` with:

- `ExtractionMetrics` dataclass: `chars`, `pages`, `table_markers`, `formula_markers`.
- `choose_extraction_strategy(metrics) -> str`: return `mineru` when `chars < max(1000, pages * 400)`, `formula_markers >= 50`, or `table_markers >= 20`; otherwise return `lightweight`.
- `normalize_mineru_outputs(mineru_output_dir, output_dir) -> dict`: copy the best Markdown file to `text.md`, create empty `tables.md`, `equations.md`, and `figures.md` if missing, write `manifest.json`, and return the manifest.
- `extract_lightweight(pdf_path, output_dir) -> dict`: call `pdftotext -layout` when available, otherwise try `pypdf` if installed, write `text.md`, empty companion files for tables/equations/figures, and a manifest.
- `extract_pdf(pdf_path, output_dir, prefer_mineru=False, mineru_wrapper=None) -> dict`: run lightweight first unless `prefer_mineru`, then route to the bundled MinerU adapter when needed. If MinerU is needed but unavailable, write a manifest with `status: failed` and a clear reason.
- CLI arguments: `pdf`, `--output`, `--prefer-mineru`, `--no-mineru`.

- [ ] **Step 4: Run tests**

Run:

```bash
uv run pytest tests/test_extract_pdf.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit extraction routing**

Run:

```bash
git add shared/scripts/extract_pdf.py tests/test_extract_pdf.py
git commit -m "feat(extract): 添加PDF提取路由"
```

## Task 6: Classification and Knowledge-Base Query

**Files:**
- Create: `shared/scripts/classify_paper.py`
- Create: `shared/scripts/kb_query.py`
- Create: `tests/test_classify_and_query.py`

- [ ] **Step 1: Write failing classification and query tests**

Add `tests/test_classify_and_query.py`:

```python
from shared.scripts.classify_paper import classify_text, infer_year
from shared.scripts.kb_query import rank_related_papers


def test_infer_year_prefers_recent_paper_year():
    text = "Published at NeurIPS 2024. References include work from 2018 and 2020."
    assert infer_year(text) == 2024


def test_classify_machine_learning_paper():
    result = classify_text("We train a transformer neural network on ImageNet and compare against baselines.")
    assert "machine-learning" in result["domains"]
    assert "transformer" in result["keywords"]


def test_classify_systems_paper():
    result = classify_text("We design a distributed scheduler that improves latency and throughput in a cluster.")
    assert "systems" in result["domains"]


def test_rank_related_papers_scores_shared_fields():
    target = {
        "paper_id": "target",
        "classification": {"domains": ["machine-learning"], "tasks": ["classification"], "keywords": ["transformer"]},
        "evidence": {"datasets": ["ImageNet"], "metrics": ["accuracy"]},
        "critique": {"limitations": ["high compute"]},
    }
    candidates = [
        {
            "paper_id": "close",
            "classification": {"domains": ["machine-learning"], "tasks": ["classification"], "keywords": ["transformer"]},
            "evidence": {"datasets": ["ImageNet"], "metrics": ["accuracy"]},
            "critique": {"limitations": []},
        },
        {
            "paper_id": "far",
            "classification": {"domains": ["security"], "tasks": ["fuzzing"], "keywords": ["symbolic-execution"]},
            "evidence": {"datasets": [], "metrics": []},
            "critique": {"limitations": []},
        },
    ]
    ranked = rank_related_papers(target, candidates)
    assert ranked[0]["paper_id"] == "close"
    assert ranked[0]["score"] > ranked[1]["score"]
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv run pytest tests/test_classify_and_query.py -q
```

Expected: FAIL because modules do not exist.

- [ ] **Step 3: Implement classification heuristics**

Create `shared/scripts/classify_paper.py`:

- `infer_year(text) -> int | None`: find years from 1990 through current year plus one; prefer venue-like nearby mentions (`NeurIPS`, `ICML`, `ICLR`, `CVPR`, `ACL`, `SIGCOMM`, `SOSP`, `OSDI`, `USENIX`, `IEEE S&P`, `CCS`, `NDSS`); otherwise return the maximum plausible year.
- `classify_text(text) -> dict`: return `domains`, `paper_type`, `tasks`, and `keywords`.
- Include keyword maps for `machine-learning`, `systems`, `security`, `software-engineering`, `databases`, `data-mining`, and `robotics`.
- CLI: read a text file and print JSON classification.

- [ ] **Step 4: Implement KB query ranking**

Create `shared/scripts/kb_query.py`:

- `rank_related_papers(target: dict, candidates: list[dict], limit: int = 10) -> list[dict]`.
- Score shared domains, tasks, keywords, datasets, metrics, and limitation terms.
- Exclude candidates with the same `paper_id`.
- Return dictionaries with `paper_id`, `score`, and `matched_fields`.
- CLI: `python shared/scripts/kb_query.py --kb workspace/knowledge/papers --paper-id <id> --limit 10`.

- [ ] **Step 5: Run tests**

Run:

```bash
uv run pytest tests/test_classify_and_query.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit classification and query**

Run:

```bash
git add shared/scripts/classify_paper.py shared/scripts/kb_query.py tests/test_classify_and_query.py
git commit -m "feat(kb): 添加论文分类与检索"
```

## Task 7: Unified Workflow CLI

**Files:**
- Create: `shared/scripts/paper_workflow.py`
- Create: `tests/test_paper_workflow.py`

- [ ] **Step 1: Write failing workflow tests**

Add `tests/test_paper_workflow.py`:

```python
import json
from pathlib import Path

from shared.scripts.paper_workflow import setup_workspace, update_state


def test_setup_workspace_creates_expected_directories(tmp_path):
    workspace = tmp_path / "workspace"
    setup_workspace(workspace)
    for relative in [
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
    ]:
        assert (workspace / relative).exists()


def test_update_state_records_stage(tmp_path):
    workspace = tmp_path / "workspace"
    setup_workspace(workspace)
    update_state(workspace, "paper-1", "ingested", {"path": "x.pdf"})
    data = json.loads((workspace / "state/papers.json").read_text(encoding="utf-8"))
    assert data["papers"]["paper-1"]["stages"]["ingested"]["path"] == "x.pdf"
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
uv run pytest tests/test_paper_workflow.py -q
```

Expected: FAIL because `paper_workflow.py` does not exist.

- [ ] **Step 3: Implement workflow helpers**

Create `shared/scripts/paper_workflow.py` with:

- `setup_workspace(workspace: Path) -> None`.
- `update_state(workspace: Path, paper_id: str, stage: str, payload: dict) -> None`.
- `load_state(workspace: Path) -> dict`.
- CLI subcommands:
  - `setup --workspace workspace`
  - `validate --workspace workspace`
  - `query --workspace workspace --paper-id <id>`
  - `status --workspace workspace`
- Keep `ingest` as a CLI subcommand that wires together extraction and classification only when a real local PDF path is provided. It should create an initial memory JSON from the template and set `status.ingested = true`.

- [ ] **Step 4: Run workflow tests**

Run:

```bash
uv run pytest tests/test_paper_workflow.py -q
```

Expected: PASS.

- [ ] **Step 5: Run full deterministic test suite**

Run:

```bash
uv run pytest -q
```

Expected: PASS except `tests/test_repo_structure.py` may still pass from Task 2.

- [ ] **Step 6: Commit workflow CLI**

Run:

```bash
git add shared/scripts/paper_workflow.py tests/test_paper_workflow.py
git commit -m "feat(workflow): 添加论文工作流CLI"
```

## Task 8: Replace Generated Skill Bodies with Final Procedures

**Files:**
- Modify: `skills/paper-research-workflow/SKILL.md`
- Modify: `skills/paper-ingest-classifier/SKILL.md`
- Modify: `skills/paper-plain-explainer/SKILL.md`
- Modify: `skills/paper-expert-reader/SKILL.md`
- Modify: `skills/paper-code-reproducer/SKILL.md`
- Modify: `skills/paper-knowledge-base/SKILL.md`
- Modify: `skills/paper-innovation-miner/SKILL.md`
- Create: `tests/test_skill_content.py`

- [ ] **Step 1: Write failing skill content tests**

Add `tests/test_skill_content.py`:

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def test_workflow_skill_mentions_all_child_skills_and_shared_cli():
    text = read_skill("paper-research-workflow")
    for name in [
        "paper-ingest-classifier",
        "paper-plain-explainer",
        "paper-expert-reader",
        "paper-code-reproducer",
        "paper-knowledge-base",
        "paper-innovation-miner",
    ]:
        assert name in text
    assert "shared/scripts/paper_workflow.py" in text


def test_ingest_skill_uses_bundled_pdf_references_not_external_skills():
    text = read_skill("paper-ingest-classifier")
    assert ".agents/skills/" not in text
    assert "shared/references/pdf-processing.md" in text
    assert "shared/references/mineru-local.md" in text
    assert "workspace/extracted/<paper-id>/" in text


def test_each_skill_mentions_shared_contracts():
    for name in [
        "paper-research-workflow",
        "paper-ingest-classifier",
        "paper-plain-explainer",
        "paper-expert-reader",
        "paper-code-reproducer",
        "paper-knowledge-base",
        "paper-innovation-miner",
    ]:
        text = read_skill(name)
        assert "shared/templates" in text
        assert "workspace/knowledge/papers/<paper-id>.json" in text
```

- [ ] **Step 2: Run tests and verify generated bodies fail**

Run:

```bash
uv run pytest tests/test_skill_content.py -q
```

Expected: FAIL because generated skill bodies do not yet contain final procedures.

- [ ] **Step 3: Write final `paper-research-workflow` body**

Use this frontmatter pattern:

```yaml
---
name: paper-research-workflow
description: Use when the user asks to read, process, classify, explain, reproduce, store, query, or mine innovation ideas from local computer-science research papers. Orchestrates the paper research skill suite across ingest, plain explanation, expert reading, reproduction planning, knowledge-base updates, and innovation mining.
---
```

Body requirements:

- State that it is the orchestrator.
- Route full reads through all six child skills.
- Use `shared/scripts/paper_workflow.py` for setup, status, validation, and deterministic state updates.
- Mention the default workspace layout.
- Mention stopping conditions and reporting.

- [ ] **Step 4: Write final child skill bodies**

For each child skill, use concise frontmatter descriptions that include concrete trigger contexts. Each body must include:

- Inputs it expects.
- Outputs it writes.
- Shared templates it must use.
- Shared scripts it may run.
- Required updates to `workspace/knowledge/papers/<paper-id>.json`.
- Failure/uncertainty handling.

Specific required notes:

- `paper-ingest-classifier`: mention `shared/references/pdf-processing.md`, `shared/references/mineru-local.md`, and the bundled extraction scripts; write `workspace/extracted/<paper-id>/manifest.json`.
- `paper-plain-explainer`: use `shared/templates/paper-card.md`; explain claims clearly; include terminology.
- `paper-expert-reader`: distinguish paper claims from inference; extract assumptions, evidence quality, limitations, and innovation seeds.
- `paper-code-reproducer`: produce reproduction plan, not full implementation by default.
- `paper-knowledge-base`: validate memory; detect duplicates; keep paths stable.
- `paper-innovation-miner`: use `shared/scripts/kb_query.py`; produce innovation brief with caveats about novelty.

- [ ] **Step 5: Run skill content tests**

Run:

```bash
uv run pytest tests/test_skill_content.py -q
```

Expected: PASS.

- [ ] **Step 6: Validate each skill folder with official validator**

Run:

```bash
python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/paper-research-workflow
python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/paper-ingest-classifier
python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/paper-plain-explainer
python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/paper-expert-reader
python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/paper-code-reproducer
python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/paper-knowledge-base
python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/paper-innovation-miner
```

Expected: each command reports success.

- [ ] **Step 7: Commit final skill bodies**

Run:

```bash
git add skills tests/test_skill_content.py
git commit -m "feat(skills): 完成论文研究技能流程说明"
```

## Task 9: End-to-End Fixtures, Validation, and Documentation Cleanup

**Files:**
- Create: `tests/fixtures/memory/*.json`
- Create: `tests/test_end_to_end_contract.py`
- Modify: `docs/superpowers/specs/2026-05-06-paper-research-skills-design.md` only if implementation reveals a necessary clarification.

- [ ] **Step 1: Create fixture memories**

Create at least two valid memory fixtures under `tests/fixtures/memory/`:

- `2024-transformer-systems-a11111.json`: machine-learning/systems overlap.
- `2023-security-fuzzing-b22222.json`: security/software-engineering overlap.

Both fixtures must validate against `paper-memory.schema.json` and include non-empty `classification`, `evidence`, `critique`, and `innovation` fields.

- [ ] **Step 2: Write end-to-end contract tests**

Add `tests/test_end_to_end_contract.py`:

```python
from pathlib import Path

from shared.scripts.kb_query import load_memories, rank_related_papers
from shared.scripts.paper_workflow import setup_workspace
from shared.scripts.validate_memory import validate_memory


ROOT = Path(__file__).resolve().parents[1]


def test_fixture_memories_validate():
    schema = ROOT / "shared/schemas/paper-memory.schema.json"
    for path in sorted((ROOT / "tests/fixtures/memory").glob("*.json")):
        errors = validate_memory(__import__("json").loads(path.read_text(encoding="utf-8")), schema)
        assert errors == []


def test_kb_query_loads_fixture_memories(tmp_path):
    workspace = tmp_path / "workspace"
    setup_workspace(workspace)
    kb_dir = workspace / "knowledge/papers"
    for fixture in (ROOT / "tests/fixtures/memory").glob("*.json"):
        (kb_dir / fixture.name).write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
    memories = load_memories(kb_dir)
    assert len(memories) == 2
    ranked = rank_related_papers(memories[0], memories[1:])
    assert ranked
    assert ranked[0]["score"] >= 0
```

- [ ] **Step 3: Run all tests**

Run:

```bash
uv run pytest -q
```

Expected: PASS.

- [ ] **Step 4: Run official skill validators again**

Run the seven `quick_validate.py` commands from Task 8.

Expected: PASS.

- [ ] **Step 5: Check working tree and diff**

Run:

```bash
git status --short
git diff --stat
```

Expected: only intended files are modified or untracked.

- [ ] **Step 6: Commit final fixtures and validation**

Run:

```bash
git add tests/fixtures tests/test_end_to_end_contract.py docs/superpowers/specs/2026-05-06-paper-research-skills-design.md
git commit -m "test(contract): 添加论文技能端到端契约测试"
```

## Final Verification

- [ ] Run all tests:

```bash
uv run pytest -q
```

- [ ] Validate all skills:

```bash
for skill in skills/paper-*; do python /home/fate/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"; done
```

- [ ] Smoke-test workspace setup:

```bash
python shared/scripts/paper_workflow.py setup --workspace /tmp/paper-research-skills-smoke
python shared/scripts/paper_workflow.py status --workspace /tmp/paper-research-skills-smoke
```

- [ ] Confirm no unexpected working-tree changes:

```bash
git status --short
```

## Spec Coverage Self-Review

- Seven skills: covered by Tasks 2 and 8.
- Shared schemas and templates: covered by Task 3.
- Local PDF extraction with lightweight and MinerU routing: covered by Task 5.
- File-based knowledge base and paper memory schema: covered by Tasks 3, 4, 7, and 9.
- Classification, archive path, and paper ID contracts: covered by Tasks 4, 6, and 7.
- Plain explanation, expert reading, reproduction plan, and innovation mining procedures: covered by Task 8.
- Knowledge-base retrieval and innovation support: covered by Tasks 6 and 9.
- Validation and testing: covered throughout Tasks 1 through 9 and Final Verification.
