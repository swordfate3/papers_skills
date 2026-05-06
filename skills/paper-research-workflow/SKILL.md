---
name: paper-research-workflow
description: Use when the user asks to read, process, classify, explain, reproduce, store, query, or mine innovation ideas from local computer-science research papers. Orchestrates the paper research skill suite across ingest, plain explanation, expert reading, reproduction planning, knowledge-base updates, and innovation mining.
---

# Paper Research Workflow

## Role

Act as the complete installable paper research skill suite. This single skill is the recommended `npx skills add` target and includes the scripts, schemas, templates, and references needed to run without installing the six child workflows separately.

Route natural user requests to the six internal child workflows:

- `references/child-skills/paper-ingest-classifier.md`
- `references/child-skills/paper-plain-explainer.md`
- `references/child-skills/paper-expert-reader.md`
- `references/child-skills/paper-code-reproducer.md`
- `references/child-skills/paper-knowledge-base.md`
- `references/child-skills/paper-innovation-miner.md`

Use this skill when the user asks to "read this paper", process a local PDF, update the paper knowledge base, prepare a reproduction plan, or find innovation ideas from stored papers.

## Shared Contracts

Use `scripts/paper_workflow.py` for setup, status, validation, query, and deterministic state updates.

Use `templates/` for output shape. Use `schemas/` for validation. Use `references/` for PDF extraction, MinerU, and child workflow guidance. Every paper should maintain canonical memory at:

```text
workspace/knowledge/papers/<paper-id>.json
```

Default workspace:

```text
workspace/inbox/
workspace/extracted/<paper-id>/
workspace/knowledge/cards/
workspace/knowledge/expert-readings/
workspace/knowledge/reproductions/
workspace/knowledge/innovations/
workspace/state/papers.json
```

## Routing

For a full paper read:

1. Run or instruct setup with `python scripts/paper_workflow.py setup --workspace workspace`.
2. Read `references/child-skills/paper-ingest-classifier.md` to extract, classify, archive, and create initial memory.
3. Read `references/child-skills/paper-plain-explainer.md` to create the plain-language card.
4. Read `references/child-skills/paper-expert-reader.md` to create the expert reading and innovation seeds.
5. Read `references/child-skills/paper-code-reproducer.md` to create the reproduction plan.
6. Read `references/child-skills/paper-knowledge-base.md` to update and validate memory.
7. Read `references/child-skills/paper-innovation-miner.md` only when the user asks for related papers or innovation directions.

For partial requests, call only the matching child skill and keep `workspace/knowledge/papers/<paper-id>.json` updated.

## Stop Conditions

Stop and report clearly when the local PDF is missing, extraction fails, schema validation fails, or the knowledge base has too few related papers for useful innovation mining. Do not invent missing tables, formulas, code availability, or benchmark results.
