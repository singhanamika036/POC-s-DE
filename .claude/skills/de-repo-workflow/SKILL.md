---
name: de-repo-workflow
description: Use when inspecting or editing this repository. Covers session startup, safe editing, the approval gate before any commit, and the diff review checklist. Trigger on requests to change files in POC-s-DE, review a diff, or start work on a POC.
---

# Repo workflow

Full rules are in `CLAUDE.md`. This skill is the checklist to run through.

## 1. Start of session
1. Confirm the working directory is `~/Documents/POC-s-DE` and the branch is correct (`git branch --show-current`).
2. Run `git status`. If there are uncommitted changes you did not make, stop and report them.
3. Read `memory/PROJECT_MEMORY.md`, `memory/LESSONS_LEARNED.md`, and any `docs/rca/*.md` related to the task.

## 2. Before editing
- Read every file you intend to change, in full, in this session.
- Find the existing pattern (naming, layout, test style) and follow it.
- Keep the change small. Do not refactor or rename working code unless asked.

## 3. After editing
- Run the POC's tests, linter and formatter, and paste the real summary lines.
- Review the diff as a senior engineer:
  - Regressions in existing behaviour?
  - Any secret, token, key or client data in the change?
  - Unnecessary complexity or new dependencies?
  - Docs and tests updated to match?
- Record results in `docs/VALIDATION.md`.

## 4. Commit gate (hard rule)
- Do not stage, commit, push, merge, reset or delete without explicit approval for that action.
- Show `git status` and `git diff --stat`, then wait.
- The deny-list in `.claude/settings.json` blocks these commands as a backstop. Do not try to get around it, for example with `git -c` or a different shell.

## 5. Report
Files created, files modified, decisions, commands run, test results, limitations, and the diff summary.
