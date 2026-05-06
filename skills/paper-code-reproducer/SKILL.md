---
name: paper-code-reproducer
description: Use when the user wants to reproduce, implement, port, benchmark, or plan code for a computer-science research paper. Produces reproduction difficulty, minimum viable reproduction, dependencies, data needs, metrics, commands, risks, and prototype tasks.
---

# Paper Code Reproducer

## Inputs

Read extracted paper artifacts and memory:

```text
workspace/extracted/<paper-id>/text.md
workspace/knowledge/papers/<paper-id>.json
```

Expert readings under `workspace/knowledge/expert-readings/<paper-id>.md` are useful when available.

## Output

Use `shared/templates/reproduction-plan.md` and write:

```text
workspace/knowledge/reproductions/<paper-id>.md
```

Update `workspace/knowledge/papers/<paper-id>.json`:

- `reproduction.code_available`
- `reproduction.difficulty`
- `reproduction.compute_need`
- `reproduction.data_need`
- `reproduction.minimum_viable_reproduction`
- `reproduction.blocking_unknowns`
- `artifacts.reproduction_plan`
- `status.reproduction_planned`

## Default Behavior

Produce a reproduction plan, not a full implementation, unless the user explicitly asks to write code. When implementing code, start a normal coding workflow in the target repository and follow its tests, dependencies, and style.

## Reproduction Analysis

Identify required datasets, checkpoints, hardware, environment, dependencies, metrics, baselines, ablations, expected sanity checks, and likely blockers. Mark uncertain items as blocking unknowns instead of guessing.

## Shared Contracts

Use `shared/templates` and keep `workspace/knowledge/papers/<paper-id>.json` as the canonical machine-readable record.
