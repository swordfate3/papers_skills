---
name: paper-innovation-miner
description: Use when the user wants to retrieve related papers from the file knowledge base, compare papers, find innovation collisions, or propose new research directions from stored computer-science paper memories.
---

# Paper Innovation Miner

## Inputs

Read canonical paper memories from:

```text
workspace/knowledge/papers/<paper-id>.json
```

Use the target paper memory plus related memories from the same file knowledge base.

## Retrieval

Use the transparent file-based query helper:

```bash
python shared/scripts/kb_query.py --kb workspace/knowledge/papers --paper-id <paper-id> --limit 10
```

Version 1 retrieves by structured fields: domains, tasks, keywords, datasets, metrics, and limitations. It does not require embeddings or a vector database.

## Output

Use `shared/templates/innovation-brief.md` and write:

```text
workspace/knowledge/innovations/<innovation-id>.md
```

Update `workspace/knowledge/papers/<paper-id>.json` when a target paper gains durable related-paper links or innovation seeds.

## Innovation Brief Standard

Include source papers, shared problem or tension, complementary mechanisms, concrete hypothesis, why it might work, minimum experiment, risks, and falsification conditions.

Do not claim verified novelty. State that the output is an ideation artifact and still needs literature search.

## Shared Contracts

Use `shared/templates` for structure and keep durable links in `workspace/knowledge/papers/<paper-id>.json`.
