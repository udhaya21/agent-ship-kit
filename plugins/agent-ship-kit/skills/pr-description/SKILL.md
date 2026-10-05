---
name: pr-description
description: Write a PR title and description from the branch's real diff, honoring the repo's PR template and its existing PR conventions. Use when asked to create, open or raise a PR, to write a PR description, or when a branch is ready to push.
---

# PR Description

The diff explains the change; the description orients the reviewer. Write the summary a reviewer needs before opening the diff, and nothing they would learn from the diff anyway.

## Process

1. **Gather facts.** `git log` and the full diff against the merge-base with the default branch. Ticket key from the branch or request (`ABC-123/bug/...` → `ABC-123`; any `[A-Z][A-Z0-9]+-[0-9]+`). Describe only what the diff contains.
2. **Find the convention**, first match wins:
   1. A template: `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/*.md`, `docs/pull_request_template.md`. Its sections are the skeleton: fill every section and keep every checklist verbatim.
   2. The repo's own history: read 2-3 recent merged PRs, ideally from the same author or feature area (`gh pr list --state merged --limit 5 --json number,title,body`). Match their headers, title format and tone.
   3. Neither exists: use the fallback skeleton below.
3. **Write the body** by the style rules below. Exemplars of the shape: [references/exemplars.md](references/exemplars.md).
4. **Add one diagram only when the change has a shape words describe badly**: a pipeline whose stages move, a control-flow fork, a before/after tree. A ```mermaid block renders on GitHub; a ```diff block is often clearer for "this shape exists, here is what moved". Place it above the prose it replaces and delete that prose. Validate mermaid syntax, since a syntax error renders as a raw code block.
5. **Cut.** Reread against rule 1 and remove anything a reviewer reading the diff already knows. If a humanizer skill is installed, run it over the draft and re-check rule 1 afterwards, since humanizing can re-lengthen.
6. **Deliver.** Show title and body for approval. Run `gh pr create` only when asked to open the PR, and only once the branch is pushed or pushing was explicitly requested. The body carries no tool attribution footer.

## Title

Match the repo's observed convention (Conventional Commits, ticket prefix, plain sentence). No convention found: `ABC-123: Sentence-style description`, under 72 chars, or the plain description when there is no ticket.

## Fallback skeleton

```
Ticket: <ID or "No ticket">

## Description of changes

<bullets>

## How to test

<click-through steps>
```

## Style rules

1. **Concise wins every conflict.** One bullet = one change = one line. Target 2-4 bullets in the description; past 6 is an essay. Sub-headings exist for genuinely unrelated concerns, never to fit more bullets in. Verification narrative, test counts and "how I checked" belong in commit messages. The one thing worth pulling out is a decision the reviewer may want to overrule: put it in a single `> [!NOTE]` callout.
2. **Plain punctuation.** Periods, commas, colons and parentheses join clauses; two short sentences beat one long one. En dashes in numeric ranges (`3-5`) are fine.
3. **One physical line per bullet**, however long. GitHub re-wraps to the reader's width, so hard-wrapped source renders as ragged half-lines. The sole exception is checklist text the template itself wraps.
4. **Bullets lead with a past-tense verb** (Added, Updated, Removed, Refactored) stating what was done, never plans.
5. **Bug fixes go symptom → root cause → fix**, often opening "Previously, ...". The `because` clause comes before the remedy.
6. **How to test is click-through instructions to the reviewer**: open with Open/Navigate/Run (link a preview URL when one exists), close with Verify/Confirm, and include one regression check where relevant ("Verify the existing case still works").
7. **Backtick every concrete identifier**: paths, functions, components, env vars, literal values.
8. **UI changes get a `| Before | After |` screenshot table.** Scaffold it with placeholders when screenshots are not ready yet.
9. **Caveats, environment limits and reviewer instructions go in callouts** (`> [!NOTE]`, `> [!IMPORTANT]`), never buried in a paragraph.
10. **Tick checklists honestly.** Check only what was genuinely done; an unchecked box is information.
11. **Link related work inline**: prior PR URLs, "Part N" for chained work, `#NNNN` for siblings.
12. **State known gaps plainly**: what could not be tested, what is deferred, what needs a follow-up.
13. **Larger features** may use bold-label bullets: `**Why:**`, `**How:**`, `**Trade-offs:**`, `**Tests / docs:**`.

## Sizing

Match depth to diff size and err short. A one-line chore gets the ticket line, two bullets and one test step. Releases and reverts may skip the skeleton for 1-3 plain sentences.
