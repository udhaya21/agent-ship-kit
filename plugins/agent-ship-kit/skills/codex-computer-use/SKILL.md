---
name: codex-computer-use
description: Have Codex CLI run local app verification that needs computer use, browser automation, simulators, screenshots, app launching, or an independent runtime check. Use when the user asks for Codex to test a flow, verify UI behavior, inspect a running app, capture screenshots, or confirm implemented behavior from outside the current agent's context.
---

# Codex computer use

Use Codex as a separate local verification agent when the task needs real UI interaction,
screenshots, browser, simulator or device state, or a runtime check independent of the current
context. Before the first call, load `codex-mechanics`.

Ordinary code reading, type-checking, linting and tests the current agent can run directly stay on
the current agent. Launching the requested local app, simulator or browser is in scope. Ask first
if verification would close the user's apps, change system settings, act on real accounts or data,
make purchases, publish content, or cause any other disruptive or irreversible effect.

## Workflow

1. Define a bounded verification target: starting state, steps, expected behavior, and evidence to
   capture.
2. Determine how to start the app and confirm required services or simulators are available.
3. Create a temporary artifact directory for the prompt, report and screenshots.
4. Run Codex non-interactively with workspace access and a focused prompt.
5. Read the report, inspect the produced evidence, and independently verify important claims where
   practical.
6. Report observed behavior separately from assumptions and blocked checks.

```bash
ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-computer-use.XXXXXX")"
REPORT="$ARTIFACT_DIR/report.md"
PROMPT="$ARTIFACT_DIR/prompt.md"

codex exec \
  -C "$PWD" \
  --add-dir "$ARTIFACT_DIR" \
  -s workspace-write \
  -o "$REPORT" \
  - < "$PROMPT"
```

The model comes from `~/.codex/config.toml`; add `-m <model>` only to override it. Use the
least-permissive sandbox that can complete the verification. Browser tests need
`-s danger-full-access` on macOS (see the sandbox map in `codex-mechanics`). Never use
`--dangerously-bypass-approvals-and-sandbox`. If Codex needs access outside the workspace and
artifact directory, stop and request only the specific permission required.

## Verification prompt

Write this to `$PROMPT` and replace the bracketed fields:

```text
Verify this local application behavior using computer interaction:

Target: [flow or behavior]
Starting state: [URL, app, simulator, account/test data, prerequisites]
Steps: [specific user actions]
Expected: [observable outcome]

Use only test/local accounts and data. Do not edit source files, change system settings, publish, purchase, or act on production data. Capture screenshots for key states in the provided artifact directory when useful.

Report:
- environment and starting state
- exact steps performed
- observed result versus expected result
- screenshot or artifact paths
- console, network, or runtime errors
- blockers and unverified areas
```

Include the exact startup command when Codex should launch the app. Provide test credentials only
through an existing approved mechanism such as an environment variable name; secrets never go in
the prompt or report.

## Reporting back

Treat the report as an independent observation, not proof by itself. Inspect referenced
screenshots and artifacts before citing them. State what was verified, the environment used,
deviations from expected behavior, and anything not tested.

If `codex` is unavailable, the configured model can't be selected, computer-use tooling is
missing, or the run fails, report the exact blocker and do whatever safe verification is possible
directly.
