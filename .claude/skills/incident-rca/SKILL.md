---
name: incident-rca
description: Use when debugging a failure, writing a root-cause analysis (RCA), recording lessons learned, or adding a regression test to prevent recurrence. Trigger on requests about a bug, failed run, incident, production error, or "why did this break".
---

# Incident RCA

Follow `CLAUDE.md` §7. Use this process.

## 1. Reproduce
- Get the exact error text, the command, and the input that caused it.
- Reproduce it locally before changing anything. If you cannot, say so, and say what would be needed.

## 2. Investigate
- Form a hypothesis, then test it. Record each hypothesis as confirmed or ruled out, with the evidence.
- Read the logs and the code path. Do not guess from the symptom alone.
- Check recent changes with `git log` and `git diff`.

## 3. Fix
- Make the smallest change that fixes the root cause. Do not fix symptoms in a way that hides the cause.
- Add a regression test that fails before the fix and passes after it. Record the actual result of both runs.

## 4. Write the RCA
- Copy `docs/rca/TEMPLATE.md` to `docs/rca/YYYY-MM-DD-short-slug.md`.
- Fill in every section. Write "unknown" where something was not verified. Do not invent a cause.

## 5. Capture the lesson
- If the lesson is reusable, add a short entry to `memory/LESSONS_LEARNED.md`.
- If it changes a design choice, add an entry to `memory/TECHNICAL_DECISIONS.md`.

## 6. Verify
- Re-run the full test suite and record the results in `docs/VALIDATION.md`.
