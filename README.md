# Paper Research Workflow Skill

Install the complete paper-reading workflow as one self-contained skill:

```bash
npx skills add <owner>/<repo> --skill paper-research-workflow
```

The installable skill is:

```text
skills/paper-research-workflow/
```

It includes its own scripts, schemas, templates, and references. The six child workflows are bundled as internal references under:

```text
skills/paper-research-workflow/references/child-skills/
```

## Quick Smoke Test

After installation, from the installed `paper-research-workflow` skill directory:

```bash
python scripts/paper_workflow.py setup --workspace workspace
python scripts/paper_workflow.py status --workspace workspace
```

To ingest a normal local PDF without MinerU:

```bash
python scripts/paper_workflow.py ingest /path/to/paper.pdf --workspace workspace --no-mineru
```

For complex PDFs, install MinerU on `PATH` or provide a wrapper:

```bash
MINERU_TO_MD=/path/to/mineru_to_md.sh python scripts/paper_workflow.py ingest /path/to/paper.pdf --workspace workspace
```

## Runtime Notes

- Lightweight extraction uses `pdftotext -layout` when available.
- If `pdftotext` is unavailable, the extractor tries `pypdf` when installed.
- MinerU is optional and is not bundled as an engine; this repo bundles only the adapter.
