# Paper Research Skills Design

## Goal

Build a semi-automated paper-reading skill suite for computer science, AI, machine learning, systems, and security papers. The suite accepts local PDFs, classifies and stores them, explains papers plainly, performs expert reading, supports code reproduction planning, writes structured results into a file-based knowledge base, and mines the knowledge base for new innovation ideas.

The first version publishes one installable skill: `paper-research-workflow`. It bundles six internal child workflows as references:

- `references/child-skills/paper-ingest-classifier.md`: read PDFs, extract metadata/text, classify, and archive papers.
- `references/child-skills/paper-plain-explainer.md`: produce clear, beginner-friendly explanations.
- `references/child-skills/paper-expert-reader.md`: perform expert reading and extract assumptions, limitations, insights, and reusable ideas.
- `references/child-skills/paper-code-reproducer.md`: convert papers into reproduction plans and minimal code prototype tasks.
- `references/child-skills/paper-knowledge-base.md`: write and validate file-based paper memory.
- `references/child-skills/paper-innovation-miner.md`: retrieve related papers from the knowledge base and propose innovation directions.

## Scope

Version 1 supports local PDF input only. Users place PDFs under `workspace/inbox/` or pass a local PDF path. The system may preserve fields for DOI, arXiv ID, and source URL, but it does not download papers or call external metadata APIs in the first version.

The knowledge base is file-based: Markdown plus JSON/YAML. It is designed to be Git-friendly, easy to inspect, and easy to migrate later to SQLite or a vector database.

The first domain focus is code-related research papers: CS, AI, ML, systems, security, software engineering, data mining, databases, robotics, and adjacent computational fields. The reproduction workflow is therefore centered on tasks, datasets, metrics, baselines, ablations, implementation difficulty, and minimum viable reproduction.

## Non-Goals

- Do not build a Web panel in version 1.
- Do not require a vector database in version 1.
- Do not automatically download papers from DOI, arXiv, OpenReview, ACM, IEEE, or other websites.
- Do not attempt full automatic paper reproduction. The reproduction skill produces plans, scaffolding guidance, risk analysis, and optionally bounded prototype tasks.
- Do not make every skill independently invent its own schema. Shared schemas and templates are mandatory.

## Architecture

Use one self-contained installable skill. This avoids `npx skills add` installing a child skill without its shared runtime resources.

```text
skills/
  paper-research-workflow/
    SKILL.md
    agents/openai.yaml
    scripts/
    schemas/
    templates/
    references/
      child-skills/
```

`SKILL.md` contains concise orchestration instructions. `references/child-skills/` contains the six specialized workflows. Skill-local scripts handle deterministic operations such as directory setup, PDF extraction routing, schema validation, state updates, and knowledge-base lookup. Templates provide stable output formats.

The suite should be installable with:

```bash
npx skills add <owner>/<repo> --skill paper-research-workflow
```

## Workspace Layout

The default project workspace is:

```text
workspace/
  inbox/
  papers/
    by-domain/
    by-year/
    by-venue/
  extracted/
    <paper-id>/
      text.md
      tables.md
      equations.md
      figures.md
      manifest.json
  knowledge/
    papers/
      <paper-id>.json
    cards/
      <paper-id>.md
    expert-readings/
      <paper-id>.md
    reproductions/
      <paper-id>.md
    innovations/
      <innovation-id>.md
  state/
    papers.json
```

`workspace/inbox/` is the human-facing drop zone. `workspace/papers/` contains archived copies or links organized by domain, year, and venue. `workspace/extracted/` contains normalized extraction outputs. `workspace/knowledge/` is the durable paper memory and reading output store. `workspace/state/papers.json` tracks workflow progress.

## Data Contracts

### Paper ID

Every paper receives a stable `paper_id` derived from normalized title, year, and a short hash when needed:

```text
<year>-<short-title-slug>-<hash>
```

The ID must remain stable after the paper enters the knowledge base. If metadata improves later, update the memory fields but do not rename the ID unless the user explicitly requests a migration.

### Paper Memory

Every processed paper must produce:

```text
workspace/knowledge/papers/<paper-id>.json
```

Required fields:

```json
{
  "paper_id": "2025-example-paper-a1b2c3",
  "title": "",
  "authors": [],
  "year": null,
  "venue": "",
  "source": {
    "input_path": "",
    "archived_path": "",
    "doi": "",
    "arxiv_id": "",
    "source_url": ""
  },
  "classification": {
    "domains": [],
    "paper_type": "",
    "tasks": [],
    "keywords": []
  },
  "core": {
    "problem": "",
    "motivation": "",
    "method": "",
    "contributions": [],
    "claimed_results": []
  },
  "evidence": {
    "datasets": [],
    "metrics": [],
    "baselines": [],
    "main_tables": [],
    "ablations": []
  },
  "critique": {
    "assumptions": [],
    "limitations": [],
    "failure_modes": [],
    "threats_to_validity": []
  },
  "reproduction": {
    "code_available": null,
    "difficulty": "unknown",
    "compute_need": "unknown",
    "data_need": "unknown",
    "minimum_viable_reproduction": "",
    "blocking_unknowns": []
  },
  "innovation": {
    "innovation_seeds": [],
    "transferable_ideas": [],
    "related_paper_ids": []
  },
  "artifacts": {
    "plain_explanation": "",
    "expert_reading": "",
    "reproduction_plan": ""
  },
  "status": {
    "ingested": false,
    "explained": false,
    "expert_read": false,
    "reproduction_planned": false,
    "kb_validated": false
  }
}
```

Schema files in `schemas/` define validation requirements. Markdown outputs may contain richer prose, but JSON memory is the canonical machine-readable record.

## Skill Responsibilities

### paper-research-workflow

The orchestration skill routes user requests and runs the complete or partial workflow. It should:

- Detect whether the user wants ingest, explanation, expert reading, reproduction, knowledge-base update, or innovation mining.
- Prefer the full pipeline when the user asks to "read this paper" without a narrower instruction.
- Use `scripts/paper_workflow.py` as the CLI entry when deterministic state updates are needed.
- Keep the user informed about which stage is running and where outputs are written.
- Stop and report extraction failures, missing PDFs, schema validation failures, or insufficient knowledge-base coverage.

### paper-ingest-classifier

This skill handles local PDF reading and classification. Its PDF handling must be bundled with this suite so the skill package works on machines that do not have the author's personal skill directory.

- Use `references/pdf-processing.md` and `scripts/extract_pdf.py` for normal text-based PDFs: `pdftotext -layout` first, then `pypdf` when available.
- Use `references/mineru-local.md` and `scripts/mineru_to_md.sh` for scanned, formula-heavy, table-heavy, multi-column, or complex layout PDFs.
- Allow users to set `MINERU_TO_MD=/path/to/wrapper` when they already have a local MinerU wrapper. Do not make online MinerU API calls by default.

It writes normalized extraction outputs under `workspace/extracted/<paper-id>/` and updates the initial paper memory fields.

### paper-plain-explainer

This skill produces a beginner-friendly Markdown card. It should explain:

- What problem the paper solves.
- Why the problem matters.
- What the key idea is.
- How the method works in simple language.
- What evidence supports the claim.
- What a non-expert should remember.

It avoids excessive jargon and includes a short terminology section when the paper is mainly English.

### paper-expert-reader

This skill produces a deeper expert reading. It should extract:

- Hidden assumptions.
- Key technical mechanism.
- Experimental evidence quality.
- Baseline and ablation adequacy.
- Limitations and likely failure modes.
- Connections to other methods.
- Reusable design patterns.
- Innovation seeds.

It must distinguish paper claims from the agent's own inference.

### paper-code-reproducer

This skill turns the paper into a reproduction plan. It should produce:

- Reproduction difficulty.
- Required datasets, checkpoints, dependencies, and compute.
- Minimum viable reproduction.
- Implementation modules.
- Experiment commands to create later.
- Metrics and expected sanity checks.
- Risks and blocking unknowns.

When asked to implement code, it should use a separate implementation cycle and follow the current repository's patterns. Version 1 does not automatically create a full reproduction repo for every paper.

### paper-knowledge-base

This skill writes, updates, and validates the file-based knowledge base. It should:

- Maintain canonical `paper-memory.json` records.
- Link Markdown reading artifacts from the JSON memory.
- Run schema validation after updates.
- Keep paths stable and relative where possible.
- Detect duplicates by title, DOI, arXiv ID, and content hash.

### paper-innovation-miner

This skill retrieves related papers from the file-based knowledge base and proposes innovation directions. Version 1 uses structured fields, keywords, domains, tasks, datasets, metrics, methods, and limitations rather than embeddings.

It should produce innovation briefs that include:

- Source papers.
- Shared problem or tension.
- Complementary mechanisms.
- Concrete new hypothesis.
- Why the idea might work.
- Minimal experiment.
- Risks and falsification conditions.

It should avoid claiming novelty without caveats. The output is an ideation artifact, not a literature-proof novelty claim.

## Shared Scripts

Version 1 should include these scripts:

- `scripts/paper_workflow.py`: unified CLI for setup, ingest, explain, expert-read, reproduce, validate, and mine.
- `scripts/extract_pdf.py`: route normal PDFs to lightweight extraction and complex PDFs to MinerU.
- `scripts/classify_paper.py`: classify paper domains, paper type, tasks, keywords, and archive path.
- `scripts/kb_query.py`: retrieve candidate related papers from JSON memory.
- `scripts/validate_memory.py`: validate JSON memory files against schemas.

Scripts should be deterministic helpers. They should not replace the agent's reading and reasoning; they prepare files, enforce contracts, and reduce repeated boilerplate.

## Shared Templates

Version 1 should include:

- `templates/paper-memory.json`
- `templates/paper-card.md`
- `templates/expert-reading.md`
- `templates/reproduction-plan.md`
- `templates/innovation-brief.md`

Templates define required sections and frontmatter. The skills fill them with paper-specific content.

## Main Workflow

Full pipeline:

```text
PDF input
→ setup workspace
→ extract text and artifacts
→ assign paper_id
→ classify and archive
→ create/update paper memory
→ generate plain explanation
→ generate expert reading
→ generate reproduction plan
→ validate knowledge-base record
→ optionally mine related papers for innovation directions
```

Partial workflows are allowed. For example, a user may ask only for a reproduction plan for an already-ingested paper, or only for innovation mining from the existing knowledge base.

## Error Handling

For extraction failures:

- If lightweight extraction produces too little text, retry with MinerU.
- If MinerU is unavailable, write a failure entry in `workspace/state/papers.json` and tell the user what command failed.
- If formulas, tables, or figures are uncertain, record that uncertainty in `manifest.json` and in the reading outputs.

For duplicate papers:

- Do not silently overwrite existing memory.
- Reuse the existing `paper_id` when the duplicate is confidently detected.
- If uncertain, create a conflict note and ask the user before merging.

For schema failures:

- Report the invalid fields.
- Repair the memory file when the fix is obvious.
- Keep invalid files out of `kb_validated: true`.

## Testing Strategy

Use focused tests around deterministic scripts and schema integrity:

- Validate skill folder metadata and naming.
- Validate all JSON templates against schemas.
- Test `paper_id` generation stability.
- Test duplicate detection.
- Test lightweight extraction fallback decision with mocked extraction metrics.
- Test knowledge-base query ranking on sample paper memories.
- Test state transitions for full and partial workflows.

Manual forward testing should use at least two local PDFs:

- One normal text-based CS paper.
- One complex paper with tables, formulas, or multi-column layout that should route to MinerU.

## Acceptance Criteria

Version 1 is complete when:

- All seven skills exist with clear frontmatter descriptions and concise procedural bodies.
- Shared schemas, templates, and scripts exist.
- A local PDF can move from inbox to extracted artifacts, archived storage, paper memory, plain explanation, expert reading, and reproduction plan.
- The knowledge-base validator can detect missing required fields.
- The innovation miner can retrieve related papers from at least two existing paper memory files and produce a structured innovation brief.
- The design remains compatible with future SQLite or vector-search backends.
