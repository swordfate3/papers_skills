# Bundled PDF Processing

Use this reference when extracting local PDFs without assuming any external agent skills are installed.

## Lightweight Extraction

Prefer the bundled helper:

```bash
python scripts/extract_pdf.py <paper.pdf> --output <output-dir> --no-mineru
```

The helper tries:

- `pdftotext -layout` when Poppler is available.
- `pypdf` when installed and `pdftotext` is unavailable or returns no text.

The normalized output is:

```text
text.md
tables.md
equations.md
figures.md
manifest.json
```

`manifest.json` records the extraction strategy, tool, status, and simple metrics.

## When Lightweight Extraction Is Enough

Use lightweight extraction for normal text-based PDFs with enough extracted text and no heavy formula/table layout needs.

Retry with MinerU when extracted text is too short, formulas dominate, tables dominate, or the PDF appears scanned or layout-heavy.
