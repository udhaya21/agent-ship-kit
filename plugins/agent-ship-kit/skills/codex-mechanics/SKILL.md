---
name: codex-mechanics
description: How to drive Codex CLI from another agent without silent failures. Load before the first `codex exec` or `codex review` call, before using a Codex wrapper agent (such as `codex:codex-rescue` from the OpenAI Codex plugin for Claude Code), and before setting a model on any subagent or workflow step. Covers invocation, the sandbox capability map, verifying which model actually ran, and gotchas that exit 0.
---

# Codex mechanics

Reference for running Codex CLI from another agent. Whether to delegate at all lives in
`delegation-rules`; this file is the how. Read the section that matches what you are about to do.

## Before the first call

- **Check which `codex` binary is on PATH.** A stale copy (for example in `~/.local/bin`)
  shadowing the package-manager one fails every run with a version error while **exiting 0**, so it
  reads as a completed run with no report. `which -a codex` and `codex --version` settle it.
- **Keep the CLI current.** New default models need a recent CLI; a stale one warns "model
  metadata not found" and the API rejects the request. Upgrade the CLI rather than pinning an old
  model with `-m`.
- Model, reasoning effort and sandbox defaults live in `~/.codex/config.toml`. Prefer setting them
  there over per-call flags, so every caller runs the same configuration.

## Picking the path

- **One read-only answer:** `codex exec -s read-only` with a self-contained prompt.
- **Review pass:** `codex review` (see `codex-review`).
- **Runtime or UI verification:** see `codex-computer-use`.
- **Substantial delegation**, once `delegation-rules` says to delegate (parallel work, digest-only
  investigation, independent diagnosis): a Codex
  wrapper agent if your harness has one. In Claude Code with the OpenAI Codex plugin: the
  `codex:codex-rescue` subagent type, which also works as a workflow agent type.
- **Already fully specified and small:** do it on the main loop. Delegation pays for itself only on
  open-ended, larger builds.

## Running it

- **Prefer the foreground.** A backgrounded `codex exec` sometimes dies right after its first tool
  call: exit 0, a transcript ending on the tool output, and no final message, so the report never
  exists. Bound a foreground run with the calling tool's own timeout (in Claude Code: the Bash
  tool's `timeout` parameter, 10 minutes max). A `timeout` *command* prefix can kill Codex while
  still exiting 0. This is a Codex-specific exception to the general "long runs go to the background" rule in
  `delegation-rules`: a Codex job too long for the ceiling needs splitting, not backgrounding. If
  backgrounding is unavoidable, check the output file for a final message instead of trusting the
  exit code.
- **Write mode must be explicit.** Wrapper agents decide `read-only` vs `workspace-write` from the
  request, and that decision is unreliable. The failure looks like a logic bug: the run plans every
  edit, then reports each one as "not applied, write blocked". For the Codex plugin's rescue agent,
  put a literal `--write` as the first line of any prompt that should produce edits. A result that
  says the workspace is read-only means relaunch with the flag, not rephrase the ask.
- **Audit write-mode scope.** A write-mode run can change files beyond the spec and leave them out
  of its report. Diff `git status` and `git diff` against the spec you gave before accepting; treat
  any unrequested hunk as unreviewed code.

## Sandbox capability map

| Mode | Runs | Cannot run |
|---|---|---|
| `read-only` | reads, analysis | any write |
| `workspace-write` | unit tests, type-check, lint; local servers if `[sandbox_workspace_write] network_access = true` | browsers (macOS Seatbelt denies the Mach port Chromium needs, `bootstrap_check_in: Permission denied`); some TS runners such as `tsx` (IPC permission error) |
| `danger-full-access` | browser and component tests | nothing in this list |

- `tsx` in any form fails inside the sandbox. Tell the prompt not to retry variants and to hand the
  step back; run it yourself outside the sandbox.
- Browser-test delegation goes to a direct `codex exec -s danger-full-access`, not to a wrapper
  agent that hardcodes `workspace-write`. Never use `--dangerously-bypass-approvals-and-sandbox`;
  it also skips approvals and hook trust.
- **Worktrees don't compose with Codex's sandbox.** A worktree created by the calling harness is
  not where Codex works; Codex's own sandbox can land on an unrelated commit with `.git` mounted
  read-only. For branch-specific edits in an isolated worktree, use an in-family subagent that
  edits directly (in Claude Code: `Agent` with `isolation: "worktree"`). Parallel Codex
  implementation runs each still need their own checkout so edits don't collide.

## Routing models inside subagents and workflows

- **In-family models:** set the subagent or workflow step's `model` parameter directly.
- **Codex models:** use the Codex wrapper agent type, or a direct `codex exec`.
- **Never pass a `model` override alongside a Codex wrapper agent type.** The override wins and a
  plain in-family agent does the work with its own tools, with no error, still reporting
  Codex-shaped output.
- **Fallback** when the wrapper's framing doesn't fit: a thin, low-effort in-family agent writes a
  self-contained prompt, runs `codex exec` through the shell, and returns the report (with a
  schema if you need structured output).
- **Label these agents** with a model prefix (for example `codex:review-auth`). The UI shows the
  wrapper's model, so the label is the only sign of the real worker.
- Workflow token budgets count only in-family tokens; Codex work is invisible to them.

## Verify which model actually ran

The report is never evidence of who wrote it. Check at dispatch, not at report time.

- **Direct `codex exec`** prints a header with `model:`, `provider:`, the CLI version and the
  sandbox. That line is the verification; capture the log and read it.
- **A wrapper agent** leaves its own transcript (in Claude Code: a `.jsonl` under
  `~/.claude/projects/<project>/`). Search it for the `"model"` field. An in-family model name there
  means an in-family agent wearing Codex's label, which can happen even with no `model` override.
  Check within the first minute and kill it if wrong.
- Codex's own run-state files are not evidence: recent CLIs keep state in a local database, so the
  newest rollout file can be hours stale while a run is active.
- For anything that must actually run on Codex, prefer a direct `codex exec`.
