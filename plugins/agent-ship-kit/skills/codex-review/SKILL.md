---
name: codex-review
description: Get an independent code review from Codex CLI of uncommitted changes, a branch diff, a commit, a PR checkout, or a specific implementation. Use when the user asks for a Codex review, when a second-model review perspective is useful (for example the pre-push gate), or when a diff needs auditing for bugs, regressions, security issues, missing tests, or requirement mismatches.
---

# Codex review

Use Codex as an independent reviewer: a different model than the one that built the change. Read
the relevant code yourself. Treat Codex's output as evidence, not authority. Before the first call,
load `codex-mechanics`.

## Workflow

1. Identify the review target: uncommitted changes, base branch, commit SHA, PR checkout, or
   specific files.
2. Create a temporary artifact directory for the prompt and report.
3. Write a focused review prompt from the template below, adding task-specific context and the
   declared bar.
4. Run `codex review` with the matching command shape, in the foreground with a timeout.
5. Read the report and verify every important claim against the cited code or diff.
6. Report confirmed findings first; mark anything unverified.

```bash
ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")"
REPORT="$ARTIFACT_DIR/report.md"
PROMPT="$ARTIFACT_DIR/prompt.md"

# Staged, unstaged, and untracked changes.
codex -C "$PWD" review --uncommitted - < "$PROMPT" > "$REPORT"

# Current branch against a base branch.
codex -C "$PWD" review --base main - < "$PROMPT" > "$REPORT"

# A single commit.
codex -C "$PWD" review --commit <sha> - < "$PROMPT" > "$REPORT"
```

For a checked-out PR, use `--base` with its actual base branch. For specific files or an
implementation outside a natural diff, describe the exact scope in the prompt and use the closest
target. Pass exactly one of `--uncommitted`, `--base`, `--commit`. Keep the artifact directory
until the report has been read and verified.

## Review prompt

Write this to `$PROMPT`, then add requirements, expected behavior, risky areas, relevant tests,
and files needing special attention:

```text
Review these changes for bugs, regressions, missing tests, security issues, and requirement mismatches.

Prioritize findings over summary. For each finding include:
- severity
- file and line reference
- concrete failure mode
- suggested fix direction

Do not edit files. If there are no substantive findings, say so and name any residual test gaps.
```

For a pre-push gate, add the standing rules and the bar, and mandate a verdict: PASS, or a list of
violations.

## Reporting back

Inspect each cited location before relaying a finding. Explain how each confirmed issue fails in
practice, with precise file references. Re-rank severities yourself; the reviewer's ranking is a
suggestion.

If Codex finds nothing, say so, name the review target, and list residual test gaps. If `codex` is
unavailable or the command fails, report the error and get the review from another model in a
fresh context. A review by the agent that wrote the change does not satisfy the gate; say the gate
is incomplete unless a human waives it.
