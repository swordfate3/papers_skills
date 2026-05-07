# Paper Workbench Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a bundled React visual workbench for `paper-research-workflow`.

**Architecture:** Add a self-contained Vite React app under `skills/paper-research-workflow/web/`. The UI reads typed sample/workspace-shaped data, renders category navigation, three reading cards, innovation source links, and platform prompt builders for Codex/Claude Code/OpenClaw.

**Tech Stack:** React, TypeScript, Vite, Vitest, Testing Library.

---

### Task 1: Packaging Contract

**Files:**
- Modify: `tests/test_single_skill_packaging.py`
- Modify: `tests/test_skill_content.py`

- [x] **Step 1: Write failing packaging tests**

The tests assert that `web/package.json`, React source files, and docs exist inside the installable skill.

- [x] **Step 2: Run targeted tests**

Run: `uv run pytest tests/test_single_skill_packaging.py::test_visual_workbench_declares_expected_frontend_stack tests/test_skill_content.py::test_visual_workbench_documents_three_cards_and_innovation_sources -q`

Expected: fail before implementation because `web/` does not exist.

### Task 2: Web App Scaffold

**Files:**
- Create: `skills/paper-research-workflow/web/package.json`
- Create: `skills/paper-research-workflow/web/index.html`
- Create: `skills/paper-research-workflow/web/vite.config.ts`
- Create: `skills/paper-research-workflow/web/tsconfig.json`
- Create: `skills/paper-research-workflow/web/src/main.tsx`
- Create: `skills/paper-research-workflow/web/src/App.tsx`
- Create: `skills/paper-research-workflow/web/src/styles.css`

- [ ] **Step 1: Implement Vite React app**

Use TypeScript, no external UI framework, and CSS with responsive grid.

- [ ] **Step 2: Verify build**

Run: `npm install` then `npm run build` inside `skills/paper-research-workflow/web`.

### Task 3: Data And Prompt Contracts

**Files:**
- Create: `skills/paper-research-workflow/web/src/domain.ts`
- Create: `skills/paper-research-workflow/web/src/sampleData.ts`
- Create: `skills/paper-research-workflow/web/src/promptBuilder.ts`
- Create: `skills/paper-research-workflow/web/src/App.test.tsx`

- [ ] **Step 1: Define types**

Types include paper categories, reading cards, innovation briefs, source paper links, and platform task requests.

- [ ] **Step 2: Implement prompt builder**

Generate Chinese prompts for Codex, Claude Code, and OpenClaw that include `paperId`, card type, user request, and save-as-new-version guidance.

- [ ] **Step 3: Add component tests**

Assert category navigation, three cards, innovation sources, and prompt generation render.

### Task 4: Docs And Verification

**Files:**
- Modify: `README.md`
- Modify: `skills/paper-research-workflow/SKILL.md`

- [ ] **Step 1: Document web workbench**

Explain `cd skills/paper-research-workflow/web`, `npm install`, `npm run dev`, and the UI purpose.

- [ ] **Step 2: Run verification**

Run root `uv run pytest -q`, web `npm test -- --run`, and `npm run build`.
