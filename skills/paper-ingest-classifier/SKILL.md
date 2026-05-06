---
name: paper-ingest-classifier
description: Use when the user provides a local research PDF or asks to ingest, extract, classify, archive, or create initial memory for a computer-science paper. Handles lightweight PDF extraction, MinerU fallback, metadata hints, paper IDs, and workspace storage.
---

# Paper Ingest Classifier

## Inputs

Accept a local PDF path or a PDF placed under `workspace/inbox/`. Version 1 does not download from DOI, arXiv, OpenReview, ACM, IEEE, or URLs.

## Extraction Strategy

Use `.agents/skills/pdf` patterns for normal text-based PDFs: `pdftotext -layout`, `pypdf`, or `pdfplumber`.

Use `.agents/skills/mineru-doc-to-md` for scanned, formula-heavy, table-heavy, multi-column, or complex layout PDFs. Prefer its wrapper:

```bash
/home/fate/.agents/skills/mineru-doc-to-md/scripts/mineru_to_md.sh <pdf> --output <dir>
```

Treat `.agents/skills/mineru` API guidance as optional reference only. Do not make online MinerU API calls by default.

The shared implementation entry is:

```bash
python shared/scripts/paper_workflow.py ingest <pdf> --workspace workspace
```

## Outputs

Write normalized extraction artifacts to:

```text
workspace/extracted/<paper-id>/
  text.md
  tables.md
  equations.md
  figures.md
  manifest.json
```

Create or update:

```text
workspace/knowledge/papers/<paper-id>.json
```

Use `shared/templates/paper-memory.json` for the initial memory shape. Set `status.ingested` only after extraction, classification, archive path, and initial memory are written.

## Classification

Classify CS/AI/ML/systems/security papers by domains, paper type, tasks, and keywords. Prefer transparent evidence from title, abstract, method, experiments, datasets, and metrics. Keep uncertain fields empty or marked `unknown`; do not guess venue, authors, DOI, or arXiv ID without evidence.

## Failure Handling

If lightweight extraction returns too little text, retry with MinerU unless the user disabled it. If MinerU is unavailable, write `workspace/extracted/<paper-id>/manifest.json` or the incoming extraction manifest with `status: failed`, then report the command and reason.
