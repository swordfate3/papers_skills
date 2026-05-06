# Bundled MinerU Adapter

Use this reference when a local PDF needs OCR, formula/table preservation, or complex layout handling.

The portable entry point in this suite is:

```bash
scripts/mineru_to_md.sh <paper.pdf> --output <output-dir> --backend auto
```

This adapter does not assume another agent skill is installed. It supports:

- `standard-cloud`: high-quality MinerU v4 cloud parsing. Configure once with `python scripts/paper_workflow.py configure-mineru --standard-token <token>`.
- `agent-cloud`: lightweight MinerU Agent cloud parsing without a saved token.
- `local`: `mineru` command on `PATH`.

The recommended high-quality cloud flow is:

```bash
python scripts/paper_workflow.py configure-mineru --standard-token <token>
python scripts/paper_workflow.py ingest paper.pdf --prefer-mineru --mineru-backend standard-cloud
```

Token configuration is saved in `.paper-mineru.json` inside this skill directory, so later runs do not need the token again.

For automatic backend selection:

```bash
python scripts/paper_workflow.py ingest paper.pdf --prefer-mineru --mineru-backend auto
```

`auto` prefers configured high-quality cloud token, then local `mineru`, then lightweight `agent-cloud`.

Cloud MinerU requests ignore system proxy environment variables by default. Set `MINERU_USE_PROXY=1` only when the user explicitly wants MinerU requests to use their system proxy.

For MinerU standard-cloud uploads, the bundled client sends the PDF to the OSS presigned URL without adding extra `Content-Type` headers. Do not add upload headers unless MinerU returns a presigned URL that explicitly requires them, otherwise OSS may return `SignatureDoesNotMatch`.

The standard-cloud request uses `model_version: vlm` and includes a stable `data_id` derived from the local file stem so batch results can be matched back to the source paper.

This skill package no longer depends on an external MinerU wrapper path. Use the bundled cloud or local backends directly.
