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

## First-Run Rule

Before processing the first paper, check whether `.paper-workspace.json` exists in this skill directory. If it does not exist, ask the user where to create the long-term paper workspace. Do not silently create `workspace/` by default.

After the user chooses a directory, run:

```bash
python scripts/paper_workflow.py setup --workspace <chosen-dir> --save-default
```

All later paper PDFs, extraction artifacts, Markdown analyses, reproduction plans, innovation briefs, and knowledge-base JSON files must use this saved workspace unless the user explicitly overrides it.

## MinerU Cloud Rule

This skill is self-contained and must not assume another MinerU skill exists. For high-quality cloud PDF parsing, ask the user for their MinerU token the first time, then run:

```bash
python scripts/paper_workflow.py configure-mineru --standard-token <token>
```

The token is saved in `.paper-mineru.json` inside this skill directory. Later high-quality runs should use the saved config and must not ask again unless parsing reports a missing or invalid token.

Use high-quality cloud parsing with:

```bash
python scripts/paper_workflow.py ingest <pdf> --prefer-mineru --mineru-backend standard-cloud
```

If the user does not want to configure a token, use `--mineru-backend agent-cloud` for lightweight cloud parsing or let `--mineru-backend auto` choose the best available backend.

## Shared Contracts

Use `scripts/paper_workflow.py` for setup, status, validation, query, and deterministic state updates.

For later requests, use the saved default workspace unless the user explicitly overrides it with `--workspace`.

Use `templates/` for output shape. Use `schemas/` for validation. Use `references/` for PDF extraction, MinerU, and child workflow guidance. Every paper should maintain canonical memory at:

```text
workspace/knowledge/papers/<paper-id>.json
```

Workspace layout:

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

1. If no default workspace exists, ask where to create it and run `python scripts/paper_workflow.py setup --workspace <chosen-dir> --save-default`.
2. Read `references/child-skills/paper-ingest-classifier.md` to extract, classify, archive, and create initial memory.
3. Read `references/child-skills/paper-plain-explainer.md` to create the plain-language card.
4. Read `references/child-skills/paper-expert-reader.md` to create the expert reading and innovation seeds.
5. Read `references/child-skills/paper-code-reproducer.md` to create the reproduction plan.
6. Read `references/child-skills/paper-knowledge-base.md` to update and validate memory.
7. Read `references/child-skills/paper-innovation-miner.md` only when the user asks for related papers or innovation directions.

For partial requests, call only the matching child skill and keep `workspace/knowledge/papers/<paper-id>.json` updated.

## Stop Conditions

Stop and report clearly when the local PDF is missing, extraction fails, schema validation fails, or the knowledge base has too few related papers for useful innovation mining. Do not invent missing tables, formulas, code availability, or benchmark results.
