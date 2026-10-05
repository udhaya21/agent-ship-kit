---
name: delegation-rules
description: When to hand work to another agent or model, and how to bound and check it. Use before spawning any subagent, fork, workflow, background task or other-model call (Codex, a second CLI); when planning a multi-step or multi-file task; when context grows large; and before declaring delegated work done.
---

# Delegation rules: one model, skills, and a bar

Default: **one model does the work**, on high effort, using skills. Every new agent starts with an
uncached prefix and re-reads files, so routing across many models usually spends more on
coordination and re-verification than it saves. Delegate only for the reasons below.

## When to use another agent

- **Parallel, independent work.** File groups that don't depend on each other, or separate
  investigations. Serialize only across a real dependency seam (schema change, then codegen, then
  consumers); fan out the independent groups on each side. Give parallel writers isolated
  workspaces (git worktrees) when they could touch the same files. In Claude Code: `Agent` with
  `isolation: "worktree"`.
- **Digest-only analysis.** Log crunching, heavy codebase sweeps, cloud console digging, browser
  driving. Run it in a separate agent that returns **only the conclusion**, so the raw output never
  enters the main context. Verification by clicking through an app counts here too.
- **Independent review.** The builder never grades its own work. Before a push, a different model in a
  fresh context reviews the diff (with only one model available, the gate stays open until a
  human reviews or explicitly waives it) with the mandate to prove it fails the
  bar. See `codex-review`.
- **Hard, long-lived decisions** may justify your scarcest top-tier model. Routine work does not.
- **Taste-critical output** (UI, copy, API design) comes from your best-taste model, never from the
  cheapest one. Set a floor model you never go below for user-facing work.
- **Escalate sideways before up.** When one model's output falls short, try a peer before the most
  expensive tier.

**Share context, don't re-read.** Prefer a delegate that inherits the current conversation (in
Claude Code: a fork) over a fresh agent. With fresh agents, scout once and pass the digest (paths,
line numbers, excerpts) into every prompt. Pipeline over parallel-from-scratch: downstream agents
receive the previous stage's result, not a "go read X again".

## The bar: define "done" before the work starts

Adjectives are not acceptance criteria. Declare a concrete pass/fail test before building: "all
call sites migrated and the type-checker is clean", "p95 under 200ms on staging data". Can't
measure it? The first step is inventing the measuring stick. A loop (grade, close the biggest gap,
re-grade) is only valid against a declared bar, and it stops when an independent grader can't find
a gap, not when the builder says done.

## Kickoff package

Every delegation ships with, up front:

- **The bar.**
- **The floor:** the best prior artifact or trace to match and beat. Start from it, not from zero.
- **Budgets, not permission-per-use:** spend and time limits declared once.
- **Where credentials live:** pass the environment variable *name*, never the value.
- **Return conditions:** come back only when truly blocked or facing a decision only the owner can
  make.
- **Scope honesty:** if the ask is too much at once, stop and propose a smaller first slice.

## Task granularity

Split work into tasks and commits by concern: **"would reverting this alone make sense?"** If yes,
it's its own commit, however small. Bundling breaks bisectability and dilutes review. Reviewing
several small pieces in one pass is fine; the commits still split.

## Bound every delegation

An unattended agent can run for hours. The bound names the kill, not just the check.

- **Under ~10 minutes:** a real timeout on the call itself. In Claude Code: the Bash tool's
  `timeout` parameter.
- **Longer:** run it in the background and schedule a check at the expected deadline. Still
  running then means stuck: stop it, note why, relaunch with a tighter scope. In Claude Code:
  `run_in_background` plus `ScheduleWakeup`, then `TaskStop`.
- Long is fine when it is a deliberate, monitored choice; unattended is not.
- Before declaring a body of work done, check every dispatched job, not just the ones in view.

## Context budget

- Pick a handoff threshold (for example 200k tokens) and a hard stop (300k). At the threshold,
  finish the task in flight, then compact or hand off. A handoff note holds: current task, what's
  done, what's open, files and lines touched, gotchas and how they resolved, the single next
  action.
- **A new, unrelated task gets a fresh session, not a continuation.** Cache reads of a long
  context dominate the bill.
- In Claude Code, the kit's `context-guard` hook warns at both thresholds. Without it, check the
  context size yourself at natural breakpoints.

## Trusting delegated output

- **Trust facts, re-derive verdicts.** Paths and line refs from a delegate are reliable; its
  severity and keep/drop calls are not. Make those on the main loop.
- **Scope in both sides of a seam**, or a finding is a guess wearing a citation.
- **Verify both directions:** the same evidence bar for findings kept and findings dropped.
- **Verify who did the work.** A delegate's report is never evidence of which model wrote it. See
  `codex-mechanics`.

## Effort

- Main loop: high. Raise it only for genuinely hard reasoning.
- Mechanical delegates: low or medium. Verify and judge passes: high.

## Other-family models

When your orchestrator's `model` parameter only accepts one family and the model you want lives
behind its own CLI, wrap it: a thin, low-effort in-family agent writes a self-contained prompt,
runs the CLI, and returns the report. Label these agents with the real model's name (the UI shows
the wrapper's model), and budget them separately, since in-family token tracking can't see them.
Codex specifics: `codex-mechanics`.
