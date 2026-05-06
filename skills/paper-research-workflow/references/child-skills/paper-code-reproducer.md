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

Use `templates/reproduction-plan.md` and write:

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

If the user is not satisfied and asks for a more detailed reproduction path, lower-level implementation breakdown, clearer dependency analysis, or stronger risk analysis, refine the reproduction plan again rather than stopping after one pass. Support iterative refinement until the user is satisfied.

Before replacing an existing `workspace/knowledge/reproductions/<paper-id>.md`, ask whether to `overwrite` the current plan or save a `new version`. Recommended default: keep the current plan and save a new version when the user is comparing fast MVP versus full reproduction paths.

## Default Behavior

Produce a reproduction plan, not a full implementation, unless the user explicitly asks to write code. When implementing code, start a normal coding workflow in the target repository and follow its tests, dependencies, and style.

## Reproduction Analysis

Write in the selected language from the orchestrator; default Chinese. If the user switches to English mode, write the reproduction plan in English while keeping commands, package names, code identifiers, datasets, metrics, and benchmark names unchanged. If the user switches back to Chinese mode, resume Chinese output.

Identify required datasets, checkpoints, hardware, environment, dependencies, metrics, baselines, ablations, expected sanity checks, and likely blockers. Mark uncertain items as blocking unknowns instead of guessing.

## Shared Contracts

Use `templates/` and keep `workspace/knowledge/papers/<paper-id>.json` as the canonical machine-readable record.
