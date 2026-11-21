# Setup report: Claude Code guardrails and the first POC

- **Date:** 2026-11-21
- **Branch:** `claude-setup` (created from `main` at `ceb1fcf`)
- **Commits:** 5, on `claude-setup`, listed in §12. **Not pushed.** Push needs your explicit approval.

## 1. Summary

This build implements the approved plan from the earlier assessment:
- The guardrail setup for the repo: `CLAUDE.md`, `.gitignore`, project settings with deny rules, memory and RCA docs, and six project skills.
- A first POC on a new topic: deterministic data-quality checks on synthetic retail orders, with tests.
- Validation of each piece, with the actual results recorded in `docs/VALIDATION.md`.

Two things are not finished, and both need your action:
1. **Trust the workspace.** Claude Code ignores the project's allow list until you accept the trust dialog for this folder. I can't accept it for you, and changing `~/.claude.json` needs your approval.
2. **Push approval.** The commits are local on `claude-setup`. Nothing has been pushed to GitHub.

## 2. Decisions I made where your answers were not yet given

Some questions from the assessment had no answer, so I used these defaults. Please check them.

| Question | Default I used | Why |
|---|---|---|
| Skill location | Project-level (`.claude/skills/`) | Recommended. Versioned with the repo. |
| Commit approval | No commits until approved | Approved later for the first few commits. Push still needs separate approval. |
| Tool installs (gh, gitleaks, Docker, promptfoo) | Not installed | Installing system tools needs approval. Everything runs in a repo-local uv environment. |
| Connectors | None configured | Not yet chosen. |
| "New topic" | Data-quality POC on synthetic data | Your message didn't name a topic. This fits your data-engineering focus. Change it if you meant something else. |
| Repo visibility | Unknown | Not checked. Memory and RCA files would be public if the repo is. |
| Content for the repo's projects section | Unanswered | Still open from earlier. |

## 3. Files created

**Repo root and guardrails**
- `CLAUDE.md`: engineering guide, condensed from the master instructions (77 lines)
- `.gitignore`: secrets, client data, outputs, Python caches, dbt and Airflow artifacts, and editor files
- `.claude/settings.json`: allow and deny rules (see §5)

**Project skills** (`.claude/skills/<name>/SKILL.md`, each with frontmatter)
- `de-repo-workflow`: repo inspection, safe editing, the commit gate, and the diff review checklist
- `ai-agent-development`: agent design, tool schemas, approval gates, loop limits, and agent evaluations
- `rag-development`: ingestion, chunking, retrieval, citations, and evaluation
- `data-engineering`: layered pipelines, data-quality checks, dbt and Airflow, and performance
- `incident-rca`: reproduce, investigate, fix, RCA write-up, and lessons
- `fde-client-solutioning`: discovery, domain mapping, prototyping, operating model, and handover

**Memory and documentation**
- `memory/PROJECT_MEMORY.md`: current state, conventions, owner preferences, open items
- `memory/TECHNICAL_DECISIONS.md`: TD-001 to TD-006, with reasons and trade-offs
- `memory/LESSONS_LEARNED.md`: L-001 to L-006
- `docs/VALIDATION.md`: every validation run and its actual result
- `docs/SETUP_REPORT.md`: this file
- `docs/rca/README.md` and `docs/rca/TEMPLATE.md`: RCA convention and template. No RCAs yet.

**First POC: `pocs/data-quality-checks/`**
- `README.md`: purpose, checks, how to run, known defects, limitations
- `pyproject.toml`: dependencies, dev tools, ruff and pytest configuration
- `uv.lock`: locked dependency versions. Commit this when you approve.
- `src/dq/__init__.py`, `checks.py`: 9 check functions, `run_checks` and `summarise`
- `src/dq/synthetic.py`: seeded synthetic customers and orders, with optional known defects
- `src/dq/run.py`: CLI. Exit 0 if all pass, 1 otherwise. Writes `output/dq_report.json`.
- `tests/test_checks.py`: 26 tests

## 4. Files modified

- `README.md`: not touched.
- No existing project files were changed. The only edit to a file I'd already written was removing an invalid rule from `.claude/settings.json`, which is a fix to my own file.

## 5. Design decisions

Full reasoning is in `memory/TECHNICAL_DECISIONS.md`. In short:
- **Git rules are enforced by permission deny rules**, not only by CLAUDE.md, because CLAUDE.md is advice the model can ignore (TD-001).
- **Synthetic data by default**, with known defects at fixed rows, so tests can assert the exact expected failures (TD-003).
- **Deterministic checks before any LLM layer** (TD-004).
- **Every check returns `pass`, `fail` or `skipped`.** A skipped check is never reported as a pass. This is the main correctness rule in the POC.
- **Fixed reference date** (2026-11-20) instead of today's date, so results are reproducible.
- **Per-POC uv environments** (TD-006).

## 6. Commands executed

```
git status                                  # confirm clean tree
git switch -c claude-setup                  # branch only; no commit
uv sync                                     # in pocs/data-quality-checks
uv run pytest -q                            # 26 passed
uv run ruff check --fix .                   # 1 import fixed
uv run ruff format .                        # 1 file reformatted
uv run ruff check . ; uv run ruff format --check .   # both pass
uv run pytest -q                            # 26 passed (final)
uv run python -m dq.run                     # exit 0, 14 pass
uv run python -m dq.run --inject-defects    # exit 1, 6 expected fails
python3 -m json.tool .claude/settings.json  # valid
git check-ignore --no-index <paths>         # gitignore coverage
claude -p "..."                             # runtime permission checks (see VALIDATION.md)
git status / git log main..claude-setup     # final state
```

## 7. Test and validation results

Full detail is in `docs/VALIDATION.md`.

- **POC:** 26 tests pass. Lint and format pass. Clean run exits 0. Defect run exits 1, with exactly the 6 expected checks failing.
- **Deny rules:** a read of `.env` was denied. The `git reset` test was inconclusive. The `git commit` and `git push` rules were not tested live, because a failing test could create a real commit.
- **Allow list:** not active until the workspace is trusted.
- **Skills:** all six pass the frontmatter check. Trigger accuracy is not tested.

## 8. Known limitations and risks

- **Permission rules are a guardrail, not a sandbox.** A different shell, or `git -c …`, could get around the deny list. Branch protection on GitHub would be the stronger control if the repo is ever shared.
- **The allow list is inactive until the workspace is trusted** (see §1).
- **The POC uses synthetic data only**, 500 rows, with a hard-coded row-count history. It's not a performance test.
- **No dependency or secret scanning yet.** gitleaks and a vulnerability scanner are recommended, not installed.
- **The skills are written but not evaluated.** Their trigger accuracy is unknown until the skill-creator evaluation loop is run.
- **The memory and RCA files are only as current as the last session that updated them.**

## 9. Git change summary

Committed on `claude-setup` (see §12). Original file list:

```
.claude/settings.json
.claude/skills/{ai-agent-development,data-engineering,de-repo-workflow,
                fde-client-solutioning,incident-rca,rag-development}/SKILL.md
.gitignore
CLAUDE.md
docs/SETUP_REPORT.md   docs/VALIDATION.md
docs/rca/README.md     docs/rca/TEMPLATE.md
memory/LESSONS_LEARNED.md  memory/PROJECT_MEMORY.md  memory/TECHNICAL_DECISIONS.md
pocs/data-quality-checks/  (README.md, pyproject.toml, uv.lock, src/, tests/)
```

Ignored and not committed: `.venv/`, `output/`, caches, `.DS_Store`.

## 10. What I need from you

1. **Trust the workspace:** run `claude` in `~/Documents/POC-s-DE` once and accept the trust dialog. Then the allow list takes effect, and I'll re-run the deny and allow checks.
2. **Review the diff** and approve or request changes.
3. **Approve a push** if you want the branch on GitHub. Nothing has been pushed yet.
4. **Confirm the defaults** in §2, especially the "new topic" and the skill location.
5. **Tell me the repo's visibility** (public or private).
6. **Decide on tool installs:** gh, gitleaks, promptfoo, Docker.
7. **Decide on connectors:** none, GitHub, Context7, or the DuckDB-based dbt setup.
8. **Answer the open question** about what should go in the repo's projects section.

## 11. Suggested next steps (after approval)
- Add gitleaks as a pre-commit check.
- Run the skill-creator evaluation on the six skills.
- Extend the POC with an LLM step that explains the failed checks, using the JSON report as structured input, with schema validation and a prompt-injection test.

## 12. Commit history (`claude-setup`, local only, not pushed)

| Commit | Message | Contents |
|---|---|---|
| `58c3309` | chore: add Claude Code guardrails, gitignore and project permissions | `.gitignore`, `CLAUDE.md`, `.claude/settings.json` |
| `7d52aa3` | docs: add project memory, technical decisions, lessons, RCA template and validation log | `memory/`, `docs/rca/`, `docs/VALIDATION.md`, `docs/SETUP_REPORT.md` |
| `c574fe3` | feat(skills): add six project skills | `.claude/skills/*/SKILL.md` |
| `8be3199` | feat(poc): data-quality checks on synthetic retail orders | `pocs/data-quality-checks/` |
| (this commit) | docs: record commit history and mark work as committed, not pushed | `docs/SETUP_REPORT.md`, `docs/VALIDATION.md`, `memory/PROJECT_MEMORY.md` |
