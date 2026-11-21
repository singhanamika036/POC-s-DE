# Technical decisions

Each entry gives the decision, the reason, and the trade-off.

## TD-001: Enforce Git rules with permission deny-lists, not only with CLAUDE.md
- **Decision:** `.claude/settings.json` denies `git commit`, `git push` and destructive git commands. CLAUDE.md states the same rules as guidance.
- **Why:** CLAUDE.md is advisory text that the model reads. A deny-list is enforced by the Claude Code permission system, whatever the model decides.
- **Trade-off:** Deny patterns match command prefixes. `git -c ... commit` or another shell could slip past them, so the rules are a guardrail, not a sandbox. Branch protection on GitHub is a stronger control if the repo is ever shared.

## TD-002: Project-level skills in `.claude/skills/`
- **Decision:** Skills live in the repo so they're versioned with the code.
- **Why:** A global skill directory is not visible to collaborators, and the repo's conventions should travel with it.
- **Trade-off:** Skills are only active in this repo. Shared-across-repos skills would need the global directory later.

## TD-003: Synthetic data by default, no real client data
- **Decision:** The data-quality POC generates its own seeded orders and customers.
- **Why:** Real client data may be restricted by employer or client agreements. Synthetic data also gives known defects, so the checks can be tested against an expected result.
- **Trade-off:** Synthetic data does not capture real-world quirks. Validate against sanitised production-like samples before drawing conclusions about real performance.

## TD-004: Deterministic checks before any LLM layer
- **Decision:** The data-quality checks are plain Python rules with no LLM involved.
- **Why:** The §6 guideline is to prefer deterministic workflows. Rules are testable, cheap and repeatable. An LLM can later explain failures, using the structured output of these checks as input.
- **Trade-off:** Rules have to be written by hand for each new defect type.

## TD-005: pandas for tabular checks
- **Decision:** pandas is the only runtime dependency of the data-quality POC.
- **Why:** It's the standard library for tabular checks in Python, and it's quick to test locally. It is not listed in the resume, so don't claim it as an existing skill until it's used on real work.
- **Trade-off:** Memory-bound. For large data, the same rules would move to Snowflake SQL or Spark.

## TD-006: Per-POC uv environments
- **Decision:** Each POC has its own `pyproject.toml` and `.venv`.
- **Why:** POCs have different dependencies, and this keeps them isolated. uv is already installed.
- **Trade-off:** There is no shared environment. Shared code goes in `packages/` once it's needed.
