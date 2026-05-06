---
name: paper-knowledge-base
description: Use when the user asks to write, update, validate, repair, deduplicate, or inspect file-based research paper memory. Maintains Markdown and JSON/YAML outputs under the paper knowledge workspace.
---

# Paper Knowledge Base

## Role

Maintain the file-based knowledge base. The canonical machine-readable record is:

```text
workspace/knowledge/papers/<paper-id>.json
```

Markdown artifacts live under:

```text
workspace/knowledge/cards/
workspace/knowledge/expert-readings/
workspace/knowledge/reproductions/
workspace/knowledge/innovations/
```

## Shared Contracts

Use `templates/` for new JSON and Markdown files. Validate memory with:

```bash
python scripts/validate_memory.py workspace/knowledge/papers/<paper-id>.json
```

For full workspace validation, use:

```bash
python scripts/paper_workflow.py validate --workspace workspace
```

## Update Rules

Keep paths stable and relative where practical. Do not rename `paper_id` after ingestion unless the user explicitly requests a migration.

Detect duplicates using title, DOI, arXiv ID, archived path, and content hash when available. Do not silently overwrite existing memory. If a merge is uncertain, report both candidate files and ask for a decision.

For reading artifacts under `cards/`, `expert-readings/`, and `reproductions/`, do not silently replace an existing file when the user asks for refinement. Ask whether to `overwrite` the current artifact or save a `new version`. Recommended default: save a new version unless the user explicitly wants replacement.

For innovation artifacts under `innovations/`, never replace prior innovation outputs by default. Treat innovation mining as append-only history so future requests can compare previous ranked ideas. New innovation rankings should be appended as new artifacts and recorded in the paper memory without deleting older rankings.

## Failure Handling

If validation fails, report invalid fields and fix obvious structural issues. Do not set `status.kb_validated` to true until validation passes.
