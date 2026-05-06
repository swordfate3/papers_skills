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
python scripts/kb_query.py --kb workspace/knowledge/papers --paper-id <paper-id> --limit 10
```

Version 1 retrieves by structured fields: domains, tasks, keywords, datasets, metrics, and limitations. It does not require embeddings or a vector database.

## Output

Use `templates/innovation-brief.md` and write:

```text
workspace/knowledge/innovations/<innovation-id>.md
```

Update `workspace/knowledge/papers/<paper-id>.json` when a target paper gains durable related-paper links, innovation seeds, or ranked innovation candidates.

If the user asks for innovation ideas across multiple papers, generate a ranked list of reasonable innovation directions and sort them from highest to lowest score.

## Innovation Brief Standard

Write in the selected language from the orchestrator; default Chinese. If the user switches to English mode, write the innovation brief in English while keeping paper titles, method names, datasets, metrics, and benchmark names recognizable. If the user switches back to Chinese mode, resume Chinese output.

Include source papers, shared problem or tension, complementary mechanisms, concrete hypothesis, why it might work, minimum experiment, risks, and falsification conditions.

For each candidate direction, include a `score` that reflects overall reasonableness or fit, and a `rank` from highest to lowest. Explain the scoring basis briefly so the ranking is auditable.

Do not claim verified novelty. State that the output is an ideation artifact and still needs literature search.

Innovation storage must not overwrite earlier innovation results. Append each new ranked innovation result into the knowledge base and preserve prior innovation entries so later innovation mining can compare or accumulate earlier ideas. Use append-only storage for innovation ranking history.

## Shared Contracts

Use `templates/` for structure and keep durable links in `workspace/knowledge/papers/<paper-id>.json`.
