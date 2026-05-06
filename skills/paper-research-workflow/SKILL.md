---
name: paper-research-workflow
description: Use when the user asks to read, process, classify, explain, reproduce, store, query, or mine innovation ideas from local computer-science research papers. Orchestrates the paper research skill suite across ingest, plain explanation, expert reading, reproduction planning, knowledge-base updates, and innovation mining.
---

# Paper Research Workflow

## Role

Act as the orchestrator for the paper research skill suite. Route natural user requests to the six child skills:

- `paper-ingest-classifier`
- `paper-plain-explainer`
- `paper-expert-reader`
- `paper-code-reproducer`
- `paper-knowledge-base`
- `paper-innovation-miner`

Use this skill when the user asks to "read this paper", process a local PDF, update the paper knowledge base, prepare a reproduction plan, or find innovation ideas from stored papers.

## Shared Contracts

Use `shared/scripts/paper_workflow.py` for setup, status, validation, query, and deterministic state updates.

Use `shared/templates` for output shape. Every paper should maintain canonical memory at:

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

1. Run or instruct setup with `python shared/scripts/paper_workflow.py setup --workspace workspace`.
2. Use `paper-ingest-classifier` to extract, classify, archive, and create initial memory.
3. Use `paper-plain-explainer` to create the plain-language card.
4. Use `paper-expert-reader` to create the expert reading and innovation seeds.
5. Use `paper-code-reproducer` to create the reproduction plan.
6. Use `paper-knowledge-base` to update and validate memory.
7. Use `paper-innovation-miner` only when the user asks for related papers or innovation directions.

For partial requests, call only the matching child skill and keep `workspace/knowledge/papers/<paper-id>.json` updated.

## Stop Conditions

Stop and report clearly when the local PDF is missing, extraction fails, schema validation fails, or the knowledge base has too few related papers for useful innovation mining. Do not invent missing tables, formulas, code availability, or benchmark results.
