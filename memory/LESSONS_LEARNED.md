# Lessons learned

Reusable lessons only. Each entry is short.

## L-001: Approval to implement is not approval to commit
Keep the two separate. Build, validate and show the diff, then wait for an explicit commit instruction. Set this up in the permissions, not only in the notes.

## L-002: Do not declare a test passing until it runs
Run the command and paste the real summary. If the tool is missing or the run is skipped, say so.

## L-003: Use a fixed seed and known-bad data for data-quality tests
Random data gives non-repeatable results. Injecting known defects with a fixed seed lets a test assert that each check fires on exactly the defect it targets, and stays quiet on clean data.

## L-004: Keep the content and the layout in one source
When a document has to come out as both DOCX and PDF, build both from one content structure. Otherwise they drift apart. (Learned on the resume build.)

## L-005: Check that a generated document really fits its page limit
Measure the rendered output, rather than estimating. Adjust one variable at a time (font size, then margins), and measure again after each change.

## L-007: Test a permission rule with a no-op command, never with a real side effect
To check a deny rule, pick a command that does nothing if it runs by mistake. Never test `git commit` or `git push` live. If the rule is broken, the test itself creates the commit.

## L-008: Claude Code permission rules have strict syntax, and project allow-lists need a trusted workspace
- `Write(...)` is not a valid file rule. Use `Edit(...)`, which covers all file-editing tools.
- Project `permissions.allow` entries are ignored until the workspace is trusted. The session warns about it, so read the warnings after any settings change.

## L-009: Check your own test assertions, not only that the tests pass
A test that compares a value with itself passes every time. Review each assertion and ask whether it could ever fail. (Found in this build: a CLI test asserted `pass == pass`, and it was rewritten.)

## L-006: Do not hand-type exact numbers from a source document
Compare the numbers in the output against the source programmatically. Any number that is not in the source should be treated as an error.
