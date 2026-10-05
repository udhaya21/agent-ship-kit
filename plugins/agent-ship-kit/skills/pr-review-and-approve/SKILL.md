---
name: pr-review-and-approve
description: Review a teammate's PR end to end and post the verdict, approve or request changes. Use when asked to review and approve a PR, or to re-check an author's fixes and approve. For draft-only comments or a self-review of your own diff, use pr-review.
argument-hint: "[pr-number-or-url] [--draft]"
---

# PR review and approve

Target: the PR number or URL in the request. With `--draft`, step 5 prints the review instead of posting it.

**Ready to merge** is the bar every step feeds. It holds when, on the exact head SHA you reviewed:

1. Zero confirmed blockers.
2. No required check failing. Pending is fine; a known flake is fine once named in the report.
3. The PR is out of draft and authored by someone other than you. GitHub rejects approving your own PR: run the pr-review skill in self-review mode and stop.

Ready → `APPROVE`. Otherwise → `REQUEST_CHANGES`. That mapping, and the voice in step 4, are defaults: a team with its own review convention swaps them.

## 1. Pin the PR

```bash
gh pr view <n> --json number,title,author,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,mergeStateStatus,statusCheckRollup,reviews,body
git fetch origin <base> <head>
git worktree add ../pr-<n> <headRefOid>   # keeps the user's working tree untouched
```

In the worktree: `MB=$(git merge-base origin/<base> HEAD)`.

- **Spec** = the ticket named in the title or branch (`ABC-123`), read through your tracker's CLI or API. No ticket: the PR description is the spec.
- **Re-review** when `reviews` already holds a review from you: `git range-diff` the reviewed commit against the head, then check each earlier comment against the code (the author's reply is a claim, the code is the evidence), then go to step 4. All fixed: approve with "Thanks for addressing the feedback. <one specific line>. LGTM 🚀".

Done when: head SHA, merge-base, per-check CI state and spec text are all in hand.

## 2. Run both lenses

Run them in parallel when your tool supports subagents, and keep the outputs apart until step 3.

- **Team lens:** the pr-review skill in draft-review mode on the PR.
- **Two-axis lens:** a fresh pass over `$MB..HEAD` on two axes. *Standards*: does the diff follow the repo's documented conventions (its `AGENTS.md`, `CLAUDE.md`, contributing guide, lint config)? *Spec*: does it build what the spec asked for, no more and no less?

Done when: you hold the pr-review findings plus a Standards report and a Spec report.

## 3. Verify

Merge both lenses into one list, one entry per line hit. Re-derive every severity yourself: a delegated reviewer's severity is a hint.

- A blocker earns its label against the real checkout: read the enclosing function, trace every call site for reachability claims, check the installed version against the lockfile for missing-API claims.
- Green CI on the head settles whatever it executes; call those "verified by execution".
- Reuse findings ("we already have this") rank up on sight.
- A spec gap (asked for, not built) is a blocker unless the PR says it ships later.

Hand the surviving list to a validator on a different model (the codex-review skill, or any other model in a fresh context). Its whole job: CONFIRMED or REJECTED per finding, with anchor line and evidence.

Done when: every finding is CONFIRMED with a line anchor, or dropped. The verdict then follows from the bar.

## 4. Voice

Register comes from the pr-review skill, already loaded in step 2. Copy the register, write your own words.

- **Inline comments** carry everything that anchors to a line: claim, evidence, fix, in a few sentences.
- **Body** opens with one specific line of praise, then one line on what the PR does. Approvals close with `LGTM 🚀`; request-changes bodies name the blocker in one line. Each optional point is its own short paragraph ("nitpick: ...", "Worth adding ..."). The inline threads hold the detail, so the body stays plain prose.

Punctuate with commas, periods and parentheses. If a humanizer skill is installed, run it over the body and every comment.

Done when: the body is under 80 words with zero bullets and zero headers, every comment is anchored to a diff line, and no body sentence repeats an inline comment.

## 5. Post

`--draft`: print the review and stop here.

1. Re-fetch the head. If it moved, `git range-diff $MB..<reviewed> $MB..<new>` and review the delta first.
2. Build the payload as JSON from text files (shell heredocs mangle backticks), pinned to the reviewed `commit_id`. Anchor comments by matching code text against the current `gh pr diff`; stored line numbers drift.
3. `gh api -X POST /repos/{owner}/{repo}/pulls/{n}/reviews --input payload.json` with `event` = `APPROVE` or `REQUEST_CHANGES`.
4. `git worktree remove ../pr-<n>`.

A submitted state is final. Bodies stay editable (`PUT .../reviews/{id}`), inline comments too (`PATCH .../pulls/comments/{id}`).

## 6. Report

Verdict, review link, blockers (one line each), pending checks, and anything left unverified.
