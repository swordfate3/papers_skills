---
name: paper-ingest-classifier
description: Use when the user provides a local research PDF or asks to ingest, extract, classify, archive, or create initial memory for a computer-science paper. Handles lightweight PDF extraction, MinerU fallback, metadata hints, paper IDs, and workspace storage.
---

# Paper Ingest Classifier

## Inputs

Accept a local PDF path or a PDF placed under `workspace/inbox/`. Version 1 does not download from DOI, arXiv, OpenReview, ACM, IEEE, or URLs.

## Extraction Strategy

This skill must be portable. Do not assume other agent skills are installed on the user's machine.

Use the bundled reference `references/pdf-processing.md` for normal text-based PDFs. The implementation entry is `scripts/extract_pdf.py`, which tries `pdftotext -layout` and then `pypdf` when available.

Use the bundled reference `references/mineru-local.md` for scanned, formula-heavy, table-heavy, multi-column, or complex layout PDFs. The portable MinerU adapter is:

```bash
scripts/mineru_to_md.sh <pdf> --output <dir> --backend auto
```

For high-quality cloud parsing, ask the user for their MinerU token the first time and save it:

```bash
python scripts/paper_workflow.py configure-mineru --standard-token <token>
python scripts/paper_workflow.py ingest <pdf> --prefer-mineru --mineru-backend standard-cloud
```

After that, the saved `.paper-mineru.json` config allows later high-quality MinerU runs without asking again.

The shared implementation entry is:

```bash
python scripts/paper_workflow.py ingest <pdf>
```

If the user explicitly wants a different destination, pass `--workspace <other-dir>`.

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

Use `templates/paper-memory.json` for the initial memory shape. Set `status.ingested` only after extraction, classification, archive path, and initial memory are written.

## Classification

Classify CS/AI/ML/systems/security papers by domains, paper type, tasks, and keywords. Prefer transparent evidence from title, abstract, method, experiments, datasets, and metrics. Keep uncertain fields empty or marked `unknown`; do not guess venue, authors, DOI, or arXiv ID without evidence.

## Failure Handling

If lightweight extraction returns too little text, retry with MinerU unless the user disabled it. If MinerU is unavailable, write `workspace/extracted/<paper-id>/manifest.json` or the incoming extraction manifest with `status: failed`, then report the command and reason.
