# Project memory — POC-s-DE

Last updated: 2026-11-21 (branch `claude-setup`, uncommitted)

## Purpose
Working repo for Anamika Singh's POCs: AI agents, RAG, data engineering, and client-style solution prototypes. It also serves as a portfolio for Senior Data Engineer, AI Engineer, AI Platform and Forward Deployed Engineer roles.

## Current state
- Remote `origin` is https://github.com/singhanamika036/POC-s-DE, branch `main`. The only commit there is "Initial commit" with a README.
- Guardrail setup (this branch, uncommitted):
  - `CLAUDE.md`: engineering guide
  - `.gitignore`: secrets, client data, outputs, Python caches
  - `.claude/settings.json`: deny rules that block commit, push, reset, merge, rebase, checkout, restore, tag, `gh pr` create/merge, `gh repo`, `rm -rf`, and reads or edits of `.env*`, `*.pem` and `*.key`
  - `.claude/skills/`: six project skills
  - `memory/`, `docs/`: this file and the others below
- First POC: `pocs/data-quality-checks/`, a deterministic data-quality checker over synthetic retail orders.

## Architecture conventions
- `pocs/<name>/`: one folder per POC. Each has its own README, `pyproject.toml`, source and tests. Environments are per-POC uv virtualenvs (`.venv`, gitignored).
- `packages/`: code shared by more than one POC. Empty for now.
- `clients/`: client-specific work. Gitignored.
- Synthetic data is the default. Real client data needs explicit approval.

## Preferences (from owner)
- Approval to implement does not mean approval to commit. Show the diff and wait for a commit instruction.
- Document everything, and validate with real runs. Do not report a test as passing unless it ran.
- Work in small, reviewable steps.

## Open items
- **Workspace not trusted.** Claude Code ignores `permissions.allow` in `.claude/settings.json` until the owner accepts the trust dialog in this folder. Deny rules still apply. Re-test allow and deny after trusting.
- Branch `claude-setup` is uncommitted. Commit only on explicit approval.
- POC status: `pocs/data-quality-checks` is built and tested (26 tests; clean run exit 0; defect run exit 1 with the 6 expected fails). See `docs/VALIDATION.md`.
- Owner has not yet confirmed the repo's visibility (public or private). Memory and RCA files would be public if it is public.
- Owner has not yet confirmed which connectors to set up. None are configured.
- gitleaks, gh and Docker are not installed. Recommended, but not installed.
- The owner's earlier question about what should go in the repo's projects section is still open.

See also: [[TECHNICAL_DECISIONS]], [[LESSONS_LEARNED]], `docs/VALIDATION.md`, `docs/SETUP_REPORT.md`.
