---
name: paper-web-workbench
description: Use when the user asks to open, start, stop, check, debug, restart, preview, build, test, or maintain the bundled paper research Web workbench.
---

# Paper Web Workbench

## Purpose

Operate the bundled React/Vite workbench. The skill package stores a template in `web/`, but the running app must live in the user's target workspace at `<workspace>/web`. All service maintenance should target that workspace copy.

The app is data-driven: Python exports live workspace data to `<workspace>/web/public/paper-workbench-data.json`, and the frontend hot-reads that file every 5 seconds. Bundled sample data is only a fallback before the workspace JSON is available.

## When To Use

Use this when the user asks to:

- start or open the Web visualizer
- stop or restart the Web service
- check whether the workbench is running
- inspect logs after startup or build failure
- run Web tests or production build
- maintain the UI service around Codex, Claude Code, or OpenClaw paper-reading interactions

## Commands

Run from the installed `paper-research-workflow` skill directory, but always point commands at the target workspace when it is not already saved as the default.

First release the workbench into the target workspace:

```bash
python scripts/paper_workflow.py setup --workspace <workspace> --save-default
```

The helper copies the bundled template to:

```text
<workspace>/web
```

If the workbench was already released, the helper syncs updated template source files into `<workspace>/web` and preserves runtime directories:

```text
<workspace>/web/node_modules
<workspace>/web/dist
<workspace>/web/.vite
```

Refresh the hot-read data file:

```bash
python scripts/paper_workflow.py web --web-command refresh-data --workspace <workspace>
```

This writes:

```text
<workspace>/web/public/paper-workbench-data.json
```

Install npm dependencies in that target workspace copy:

```bash
cd <workspace>/web
npm install
```

Start the service in the background:

```bash
python scripts/paper_workflow.py web --web-command start --workspace <workspace> --host 127.0.0.1 --port 5173
```

Check status:

```bash
python scripts/paper_workflow.py web --web-command status --workspace <workspace>
```

`status` also refreshes `paper-workbench-data.json` before reporting service state.

Read recent logs:

```bash
python scripts/paper_workflow.py web --web-command logs --workspace <workspace> --log-lines 120
```

Stop the service:

```bash
python scripts/paper_workflow.py web --web-command stop --workspace <workspace>
```

Foreground development, build, test, and preview:

```bash
python scripts/paper_workflow.py web --web-command dev --workspace <workspace>
python scripts/paper_workflow.py web --web-command build --workspace <workspace>
python scripts/paper_workflow.py web --web-command test --workspace <workspace>
python scripts/paper_workflow.py web --web-command preview --workspace <workspace>
```

## Maintenance Rules

- Before starting, run `status`; if already running, report the existing URL instead of starting a second service.
- If `start` fails, run `logs` and report the relevant npm or Vite error.
- If dependencies are missing, tell the user to allow `npm install` in `<workspace>/web`; do not claim the service is ready.
- Prefer `start` for long-running service use and `dev` only when the user wants foreground output.
- Run `refresh-data` after a manual edit to `knowledge/` artifacts when the user wants the UI updated immediately; otherwise the next setup, ingest, start, or status command will refresh it.
- Use `stop` before changing ports or after the user says they are done with the visualizer.

## State Files

The helper records service state inside the target workspace:

```text
<workspace>/state/.paper-web-service.json
<workspace>/state/.paper-web-service.log
```

The state file stores `pid`, `url`, `host`, `port`, command, and start time. The log file stores Vite stdout/stderr for debugging.
