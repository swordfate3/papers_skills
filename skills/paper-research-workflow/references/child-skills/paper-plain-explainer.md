---
name: paper-plain-explainer
description: Use when the user wants a research paper explained in clear, beginner-friendly language, including the problem, motivation, core idea, method, evidence, limitations, and terminology. Works from extracted paper text and updates the paper knowledge base.
---

# Paper Plain Explainer

## Inputs

Read extracted paper content from `workspace/extracted/<paper-id>/text.md` and the canonical memory at:

```text
workspace/knowledge/papers/<paper-id>.json
```

If the paper is not ingested, ask the orchestrator to run `paper-ingest-classifier` first.

## Output

Use `templates/paper-card.md` and write:

```text
workspace/knowledge/cards/<paper-id>.md
```

Update `workspace/knowledge/papers/<paper-id>.json`:

- `core.problem`
- `core.motivation`
- `core.method`
- `core.contributions`
- `core.claimed_results`
- `artifacts.plain_explanation`
- `status.explained`

## Style

Write in the selected language from the orchestrator; default Chinese. If the user switches to English mode, write the paper card in English while keeping recognizable paper terms in their original language. If the user switches back to Chinese mode, resume Chinese output.

Explain the paper as if teaching a capable engineer who is new to the specific topic. Preserve paper titles, model names, dataset names, metrics, and method names in English when translation would reduce recognizability.

Separate paper claims from your explanation. Use phrases such as "论文声称" for claims and "直观理解是" for interpretation.

Include a `## 术语对照` section for English papers.

## Shared Contracts

Use `templates/` for the Markdown shape. Keep the JSON memory at `workspace/knowledge/papers/<paper-id>.json` machine-readable and concise.

If extraction quality is uncertain, include a short uncertainty note rather than pretending the text is complete.
