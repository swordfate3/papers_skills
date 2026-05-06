---
name: paper-expert-reader
description: Use when the user wants expert-level reading of a computer-science research paper, including technical mechanism, assumptions, evidence quality, baseline and ablation critique, limitations, failure modes, reusable ideas, and innovation seeds.
---

# Paper Expert Reader

## Inputs

Read:

```text
workspace/extracted/<paper-id>/text.md
workspace/extracted/<paper-id>/tables.md
workspace/extracted/<paper-id>/equations.md
workspace/knowledge/papers/<paper-id>.json
```

If the plain explanation exists, use it as context but do not copy it.

## Output

Use `templates/expert-reading.md` and write:

```text
workspace/knowledge/expert-readings/<paper-id>.md
```

Update `workspace/knowledge/papers/<paper-id>.json`:

- `evidence.datasets`
- `evidence.metrics`
- `evidence.baselines`
- `evidence.main_tables`
- `evidence.ablations`
- `critique.assumptions`
- `critique.limitations`
- `critique.failure_modes`
- `critique.threats_to_validity`
- `innovation.innovation_seeds`
- `innovation.transferable_ideas`
- `artifacts.expert_reading`
- `status.expert_read`

## Reading Standard

Write in the selected language from the orchestrator; default Chinese. If the user switches to English mode, write the expert reading in English while keeping recognizable paper terms in their original language. If the user switches back to Chinese mode, resume Chinese output.

Distinguish paper claims from your own inference. Evaluate whether experiments actually support the claims, whether baselines are strong, whether ablations isolate the proposed mechanism, and what would likely fail outside the paper's setting.

For CS/AI/ML/systems/security papers, pay special attention to datasets, metrics, compute, implementation assumptions, missing comparisons, and reproducibility signals.

## Shared Contracts

Use `templates/` for the Markdown structure. Keep canonical structured facts in `workspace/knowledge/papers/<paper-id>.json`; use Markdown for richer argumentation.
