---
name: paper-web-workbench
description: Use when the user asks to open, start, stop, check, debug, restart, preview, build, test, or maintain the bundled paper research Web workbench.
---

# Paper Web Workbench

## Purpose

Operate the bundled React/Vite workbench in `web/`. This child skill is for service lifecycle and maintenance around the visual paper workflow UI.

## When To Use

Use this when the user asks to:

- start or open the Web visualizer
- stop or restart the Web service
- check whether the workbench is running
- inspect logs after startup or build failure
- run Web tests or production build
- maintain the UI service around Codex, Claude Code, or OpenClaw paper-reading interactions

## Commands

Run from the installed `paper-research-workflow` skill directory.

Start the service in the background:

```bash
python scripts/paper_workflow.py web --web-command start --host 127.0.0.1 --port 5173
```

Check status:

```bash
python scripts/paper_workflow.py web --web-command status
```

Read recent logs:

```bash
python scripts/paper_workflow.py web --web-command logs --log-lines 120
```

Stop the service:

```bash
python scripts/paper_workflow.py web --web-command stop
```

Foreground development, build, test, and preview:

```bash
python scripts/paper_workflow.py web --web-command dev
python scripts/paper_workflow.py web --web-command build
python scripts/paper_workflow.py web --web-command test
python scripts/paper_workflow.py web --web-command preview
```

## Maintenance Rules

- Before starting, run `status`; if already running, report the existing URL instead of starting a second service.
- If `start` fails, run `logs` and report the relevant npm or Vite error.
- If dependencies are missing, tell the user to allow `npm install` in `web/`; do not claim the service is ready.
- Prefer `start` for long-running service use and `dev` only when the user wants foreground output.
- Use `stop` before changing ports or after the user says they are done with the visualizer.

## State Files

The helper records service state inside the skill directory:

```text
.paper-web-service.json
.paper-web-service.log
```

The state file stores `pid`, `url`, `host`, `port`, command, and start time. The log file stores Vite stdout/stderr for debugging.
