# Bundled MinerU Local Adapter

Use this reference when a local PDF needs OCR, formula/table preservation, or complex layout handling.

The portable entry point in this suite is:

```bash
scripts/mineru_to_md.sh <paper.pdf> --output <output-dir>
```

This adapter does not assume another agent skill is installed. It searches for a usable MinerU command in this order:

1. `MINERU_TO_MD` environment variable pointing to an executable wrapper.
2. `mineru` command on `PATH`.

If none is available, it exits with a clear error. The extraction workflow then writes `manifest.json` with `status: failed`.

For other machines, users can provide a wrapper without editing this skill:

```bash
MINERU_TO_MD=/path/to/mineru_to_md.sh python scripts/extract_pdf.py paper.pdf --output out --prefer-mineru
```
