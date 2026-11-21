# Validation log

Every result below comes from a command that was actually run. Items marked **NOT RUN** were not executed, and the reason is given.

Environment: macOS (Darwin 24.6), Python 3.15.2, uv 0.12.17, Claude Code 2.1.326. Date of runs: 2026-11-21.

## 1. Data-quality POC (`pocs/data-quality-checks`)

| Check | Command | Result |
|---|---|---|
| Install | `uv sync` | Pass. pandas 3.1.1, numpy 2.5.5, pytest 9.2.0, ruff 0.17.6 |
| Unit and integration tests | `uv run pytest -q` | **26 passed** in 0.37s, exit 0 |
| Lint | `uv run ruff check .` | Pass after one auto-fix (import order), exit 0 |
| Format | `uv run ruff format --check .` | Pass after one auto-format (line wrapping), exit 0 |
| Clean synthetic run | `uv run python -m dq.run` | 14 pass, 0 fail, 0 skipped. Exit **0** |
| Known-defect run | `uv run python -m dq.run --inject-defects` | 8 pass, **6 fail**, 0 skipped. Exit **1** |

The 6 failures in the defect run are exactly the 6 expected checks: `not_null:order_id`, `unique:order_id`, `non_negative:amount`, `allowed_values:status`, `valid_dates:order_date`, `referential:customer_id->customer_id`. The tests also assert the failing row counts for each.

### What the tests cover
- Clean data passes every check.
- Each injected defect fires its target check and no other.
- Failure paths: a missing column gives `skipped` for dependent checks and does not raise. Empty input gives a freshness **fail**, not a pass. Stale data fails freshness. All-invalid dates fail freshness.
- Blank strings count as nulls. Non-numeric amounts are counted as bad. Nulls are ignored by the uniqueness check.
- Impossible dates (such as 2026-02-31) are flagged.
- Row-count band: passes within history, fails outside it, is skipped with fewer than 3 history points, and is exact when history has zero variance.
- The generator is deterministic for a fixed seed, and it rejects `n < 60`.
- CLI exit codes: 0 for a clean run, 1 for a defect run, and the JSON report is written with the expected fields.

### Not run for the POC
- **Coverage measurement:** not run. `pytest-cov` isn't installed, and I didn't add it.
- **Dependency vulnerability scan:** NOT RUN. No scanner is installed (pip-audit would be a new dependency, so I didn't add it without approval).
- **Scale and performance:** NOT RUN. Only 500 synthetic rows were used.
- **Real data:** NOT RUN, and not planned without approval.

## 2. Claude Code guardrails (`.claude/settings.json`)

| Check | Result |
|---|---|
| Settings file is valid JSON | Pass (`python3 -m json.tool`) |
| Invalid rule removed | `Write(./.env*)` was flagged as an invalid rule type. Removed. The tool asked for `Edit(./.env*)`, which is already present. Re-check showed the warning gone. |
| Deny rule blocks reading `.env` | **Pass, observed.** Read tool returned: "File is in a directory that is denied by your permission settings." |
| Deny rule blocks `git reset --soft HEAD` | **Inconclusive.** Command was refused, but the session can't tell whether the deny rule or the default permission mode caused it. |
| Deny rule blocks `git commit` / `git push` | **NOT RUN.** Testing it live would require executing a commit or push if the rule failed. Not worth the risk. |
| Allow list is active | **NOT ACTIVE.** Claude Code reports: "Ignoring 10 permissions.allow entries from .claude/settings.json: this workspace has not been trusted." This needs an interactive trust-dialog acceptance, which I cannot do. |

**Open item:** run `claude` in `~/Documents/POC-s-DE` once and accept the trust dialog, then re-run the deny and allow checks.

Known limitation: deny rules match command prefixes. Another shell, or `git -c …`, could bypass them, so these rules are a guardrail, not a sandbox.

## 3. `.gitignore`

Checked with `git check-ignore --no-index`:
- **Ignored (correct):** `.env`, `.env.local`, `data/orders.csv`, `clients/…`, `.venv/`, `output/dq_report.json`, `*.pem`, `*credentials*`, `*accessKeys*`, `.claude/settings.local.json`.
- **Not ignored (correct):** `CLAUDE.md`, `.claude/settings.json`, all source, tests, `pyproject.toml`, `memory/`, `docs/`, and skill files.

## 4. Skills (`.claude/skills/`)

| Check | Result |
|---|---|
| Frontmatter present, `name` matches directory, `description` > 40 chars | **Pass** for all 6 skills |
| Trigger accuracy (does each skill load for the right requests?) | **NOT RUN.** That needs the skill-creator evaluation loop, which is a separate task. |
| Content review against CLAUDE.md | Done by reading. Not an automated check. |

## 5. Memory and RCA docs

- `memory/` and `docs/rca/` files were written and read back. No automated check was run. The one factual error found (an unsupported claim about pandas experience in `TECHNICAL_DECISIONS.md` TD-005) was corrected.

## 6. Git state

- Branch: `claude-setup`, created from `main` (`ceb1fcf`).
- **No commits.** No staging. No push. No remote changes.
- Untracked files are listed in `docs/SETUP_REPORT.md`.

## Summary of what is verified vs. not
- **Verified by running:** POC tests, lint, format, CLI runs in both modes, `.gitignore` coverage, JSON validity, skill frontmatter, and the `.env` read denial.
- **Not verified:** the deny rules for commit and push, the allow list (blocked by the untrusted workspace), skill triggering, and anything involving real data, scale, or security scanning.
