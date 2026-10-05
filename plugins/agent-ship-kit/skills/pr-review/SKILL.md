---
name: pr-review
description: Review code like a careful senior teammate. Two modes, self-review of your working diff before raising a PR, or drafting review comments on someone else's PR by number. Use when the user says "review my diff", "self-review", "pre-review", "review PR #N", or before opening any PR.
---

# PR review

Find what a careful senior teammate would flag, anchored to real lines, phrased the way people actually write review comments. Every finding comes from the diff in front of you and is verifiable against the checkout.

## Mode selection

- **Self-review** (default): no PR number given, or the user says "my diff" or "before I raise". Target = working tree plus staged changes against the merge-base with the default branch (`git diff $(git merge-base HEAD origin/main)...` plus uncommitted changes). Output = a local fix-list. Nothing is posted.
- **Draft-review**: the user gives a PR number or URL. Target = `gh pr diff <n>` plus `gh pr view <n>`. Output = draft comments for the user to edit and post. Post only on explicit instruction.

## Process

0. **Confirm both refs are fresh.** `git fetch origin <base> <head>`, then check each local ref resolves to the same commit as its remote (`git rev-parse <ref>` vs `git rev-parse origin/<ref>`). In draft-review mode also cross-check `gh pr view <n> --json baseRefOid,headRefOid`. A stale base makes already-merged work look like it came from the head branch; a stale head hides real commits. Every later finding depends on this.
1. **Get the diff** (per mode) and the full list of touched files.
2. **Load the rulebook.** Read [references/checklist.md](references/checklist.md). If the repo has a review overlay (`REVIEW.md` at the root, or a file named for review in `AGENTS.md` or `CLAUDE.md`), read it too; the overlay wins where they conflict.
3. **Map touched surfaces to checklist sections.** UI components: Accessibility, i18n, React, Styling. API and resolvers: API design, Error handling, Security. Utils and logic: TypeScript, Simplification, Testing. Tests: Testing. Every diff: Always check, Simplification, Comments and docs, Performance.
4. **Apply those sections to every hunk**, starting with the always-check list at the top of the checklist.
5. **Repo-context sweep.** The diff alone hides the most common findings. Search the repo before finalising:
   - **Siblings**: find the parallel places the same concern lives (sibling components, other providers, other locale or theme files). Flag logic added to one sibling that should be shared, and changes that make siblings inconsistent. When the diff consolidates a repeated pattern into a helper, search for the old inline pattern and confirm every call site moved; the missed one is usually the least visible variant.
   - **Existing helpers**: before accepting a new utility, hook, class, or config entry, search for one that already does it. "We already have this" is the most common review comment there is.
   - **Consumers of changed shared code**: find every consumer of each changed export; flag ones whose assumptions the change breaks.
   - **Convention source**: when the diff adds to a list, registry, or config, read the whole file and its neighbours. Ordering, casing, and naming live in the parts the diff does not show.
   - **Description fidelity**: extract every checkable claim in the PR description (a number, a named behaviour, "X now does Y") and confirm it exists in the code. Overclaiming and undisclosed changes are both findings.
6. **Run the forced passes** below.
7. **Verify each finding against the code.** Read the surrounding context; a rule that looks violated may be satisfied two lines up. Drop anything you cannot anchor to a concrete line.
8. **Report** in the format below.

## Forced passes

Run on every diff after the checklist sweep. Passes 2 and 3 produce an output section even when empty ("none found" is a valid entry; silence is not).

1. **Micro-simplification.** For every added or modified conditional, boolean, or inline JSX block ask: can it merge with an adjacent one? Does the expression repeat (extract a named constant)? Does something already in scope express it? Is the inline block big enough to be its own component? Point at the exact line and name the replacement.
2. **Contract-change table.** One row per change to a type, interface, schema, API field, or prop that alters shape or strictness (optional to required, nullable to non-null, widened or narrowed union, added, removed, or renamed field, new error thrown): `what changed | why (from the diff) | question to author`. A row whose "why" you cannot fill from the diff becomes a question finding. Also ask whether the kind of response is right (NotFound vs Forbidden for an authorization failure).
3. **Sibling conformance.** For every entry added to an existing list, map, enum, config, token file, or registry, check ordering, naming pattern, duplicates, and completeness across parallel files (every locale, every theme, every provider).
4. **Value-conversion arithmetic.** When values convert between systems (px to rem, design tokens to utility classes, currency minor units), recompute every converted value. If a design spec is linked and reachable, check spacing, colour, and sizing against it. On styling code go literal by literal and ask two questions: does this value match the spec, and does this class do anything at all? A utility that is not in the build, or restates the browser default, is dead code that looks live. With no spec in reach, still raise a doubtful literal as a short question.
5. **Runtime blind spots.** The diff cannot prove runtime behaviour, so look where it is weakest: measured dimensions, interactive widgets with ARIA state, shared components with other consumers, responsive, dark-mode, and RTL styling. Turn each concern into a claim about a line (the value that will be wrong, the attribute that is absent when false, the consumer that breaks). If it cannot be reduced to a line, ask a short question about intent on the line that worries you. Review code; do not assign manual QA.
6. **External-input types.** Before judging any branch, switch, truthiness check, or interpolation over a value from outside the module, resolve its real runtime type. Query params can be `string | string[]`; env vars are `string | undefined`; payloads, form data, and anything typed `any` or `unknown` upstream need one hop up to the declaration. A `switch` over an array matches no case; a template literal over an array interpolates comma-joined garbage.
7. **Markup validity.** Inline elements do not contain block elements, interactive elements do not nest, and a changed element type keeps parent and child nesting valid.
8. **Docs content.** On docs, stories, or example config: readable example titles, the most important example first, grammatical descriptions, no leftover scaffolding comments, and examples that actually run.

## Large PRs

Beyond roughly 30 to 40 changed files or a few thousand changed lines, one sequential pass under-reviews. If your agent can run parallel subagents (in Claude Code, the Agent tool), split along natural seams (component groups, logic and hooks, shared cross-cutting code, tests), run this full process on each slice, then merge.

- Get the complete changed-file list (`git diff --name-only <base>...<head>`, no path filter) before drawing boundaries. Large PRs touch shared files outside the feature folder the title names.
- Give shared cross-cutting code and its consumers a dedicated slice even when it looks small. That is where the most consequential findings tend to live.
- When merging, deduplicate identical findings into one entry citing every location, then re-rank once with the whole diff in view.

## Depth calibration

Expect roughly one substantive comment per 40 to 60 changed lines of application code (more on shared or design-system code, fewer on generated files). Far below that on a non-trivial diff means under-review: re-run the forced passes hunk by hunk. Every finding still points at a line and names a fix or a question; silence on a clean hunk is correct.

## Output format

Every finding: `path:line [severity] category: problem. Fix: <concrete fix>.`

Severity, for your own ranking: **blocking** (must fix before merge), **suggestion** (author's call), **nitpick** (never blocks), **question** (genuine uncertainty).

- **Self-review:** findings grouped by severity, blocking first, then the mandatory pass sections. End with one line: "ready to raise" or "fix blocking items first". No praise padding.
- **Draft-review:** each finding written as a postable comment, grouped by file. The severity ladder orders the list; it is not written into the comments. Write the way experienced reviewers do:
  - When the fix is mechanical, lead with a ```suggestion``` block and little prose.
  - Ask a real question or say the thing directly. A blocking issue reads as a short, pointed question ("does this still compile?", "is this passing the order id as the user id?"), not a paragraph stamped "blocking".
  - Explain the mechanism in one clause when it is not obvious. Hedge when inferring ("I believe", "this might").
  - Put `Nitpick:` on its own line above genuinely cosmetic comments; nothing else gets a label.
  - Say so briefly when a change is genuinely good.
  - Offer the set for the user to edit.

## Calibration

- An out-of-scope discovery is a follow-up ticket, not a blocking comment.
- When a rigid rule-catalog audit runs alongside this review and returns many same-category hits that contextual reading does not corroborate, fold them into one low-priority note, especially where the codebase has an established reason for the pattern. Keep any single hit a contextual reviewer independently confirms.

## Adapt to your team

The checklist is a generic default. To make reviews sound like your team and catch your repo's own traps, add a review overlay to the repo being reviewed (`REVIEW.md` at the root, or point to it from `AGENTS.md`):

- **Conventions**: house rules the checklist does not know (state library, error tracker, routing rules, token scale, ticket format).
- **Known traps**: incidents and recurring bugs, each stated as a checkable rule with the line pattern that signals it.
- **Register**: how your reviewers phrase comments (labels used, question style, suggestion blocks), described as patterns. Quoting a colleague's real comments needs their consent.

Overlay rules override the checklist where they conflict.
