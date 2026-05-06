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

Use `shared/templates` for new JSON and Markdown files. Validate memory with:

```bash
python shared/scripts/validate_memory.py workspace/knowledge/papers/<paper-id>.json
```

For full workspace validation, use:

```bash
python shared/scripts/paper_workflow.py validate --workspace workspace
```

## Update Rules

Keep paths stable and relative where practical. Do not rename `paper_id` after ingestion unless the user explicitly requests a migration.

Detect duplicates using title, DOI, arXiv ID, archived path, and content hash when available. Do not silently overwrite existing memory. If a merge is uncertain, report both candidate files and ask for a decision.

## Failure Handling

If validation fails, report invalid fields and fix obvious structural issues. Do not set `status.kb_validated` to true until validation passes.
