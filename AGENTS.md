# agent-ship-kit

Instructions for any coding agent that reads `AGENTS.md`. Copy this file into a project root, or
paste it into your tool's instructions file. If your tool loads Agent Skills (`SKILL.md`), install
the skills instead (see the README) and keep only the house rules below.

## House rules

1. **No delegation without a bar.** Every piece of delegated work carries a concrete pass/fail
   test declared before the build. Adjectives are not bars.
2. **The builder never grades its own work.** Grading goes to a different model, in a fresh
   context, pointed at the real output (pixels, running app, diff), told to prove FAIL.
3. **No hard-coded special cases in agent behavior.** Describe the behavior and let the model
   reason; don't bolt on regex filters or if-chains for individual cases.
4. **Taste-critical output comes from your strongest model.** UI, copy and API design are not
   handed to a cheaper model to save cost.
5. **One model by default.** Delegate only for parallel work, digest-only analysis, or
   independent review.
6. **Report reality.** Failing tests, skipped steps and unverified claims are stated plainly.
7. **Nothing sensitive leaves the machine.** External services get progress notes and
   screenshots, never secrets, credentials or proprietary source.

**The gate:** before any commit or push, a different model (high effort, fresh context) checks
the diff against these rules and the declared bar, and returns PASS or a list of violations.
Violations block the push until fixed or waived by a human.

## Skills

When a task matches one of these, read its `SKILL.md` first and follow it. Skills live under
`plugins/agent-ship-kit/skills/` in https://github.com/udhaya21/agent-ship-kit; if this file was
copied into a project, copy the skills you use alongside it.

| Skill | Use when |
| --- | --- |
| `delegation-rules` | Before spawning any subagent, background task or other-model call; planning multi-step work |
| `codex-mechanics` | Before the first `codex exec` / `codex review` call from another agent |
| `codex-review` | Getting an independent Codex review of a diff, branch, commit or PR |
| `codex-computer-use` | Having Codex verify a running app, browser flow or simulator |
| `create-branch` | Starting work on a ticket: `TICKET-ID/type/description` branch names |
| `commit` | Committing staged work in Conventional Commit format with a ticket key |
| `stacked-prs` | Splitting an oversized PR into a stack |
| `pr-description` | Writing a PR title and body from the real diff and the repo's template |
| `pr-review` | Self-reviewing a diff, or drafting comments on someone else's PR |
| `pr-review-and-approve` | Reviewing a PR end to end and posting approve or request changes |
| `pr-visual-snaps` | Before/after screenshots of two deployed URLs into a PR table |
| `proposal-architecture-writer` | Proposals, design docs, RFCs, decision records |
