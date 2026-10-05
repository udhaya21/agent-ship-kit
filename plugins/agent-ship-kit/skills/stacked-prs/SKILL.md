---
name: stacked-prs
description: Split one oversized pull request into a stack of smaller PRs that each build on the last, so a different set of reviewers owns each layer. Use when a PR is too large or mixes two products/surfaces, when the user says "stacked PR", "split this PR", "separate X and Y changes for reviewers", or asks to create, rebase, land, or link a stack with `gh stack`.
---

# Stacked PRs

A stack is **bottom** (based on the default branch) plus one or more layers on top, each based
on the branch below it. Each PR shows only its own layer's diff, so reviewers see their
surface and nothing else.

The stack is a **review** device. Landing it is a separate question with its own answer below,
and getting that wrong ships a half-migration to the default branch.

## Before you cut: does the bottom stand alone?

The bottom layer merges to the default branch first, so it must be a state you are willing to
have on the default branch by itself.

It usually is not. A dependency upgrade, a shared type change, a removed export: the bottom
carries the change and the top carries every call site that adapts to it. That makes the
bottom **red by construction**, which is fine for review and fatal if merged alone.

Establish, before cutting:

- What the repo's PR checks actually run. A check that runs repo-wide (a root `check`/`lint`
  script over every workspace) fails on the bottom even when the bottom's own surface is
  clean. Read the workflow triggers: a `paths:` filter scopes *which PRs run it*, never *what
  the script covers*.
- Which checks are filtered to the default branch (`pull_request: branches: [main]`). Those
  never run on any upper layer, so the combined change is only ever exercised once the top is
  merged down.
- Whether the default branch requires status checks. If it requires review only, an approved
  bottom PR is one click from shipping.

Write these findings into the PR bodies. A reviewer who does not know which red checks are
expected treats all of them as noise.

## Files that cannot be split

Some files hold state for the whole repo: a lockfile, a generated schema, a root manifest.
They are one file, so they land on one layer, and that decides where the inputs that produce
them land too. Put a manifest on the top layer while its lockfile sits on the bottom and the
bottom's `--frozen-lockfile` install fails.

Default: **every manifest and its lockfile go on the bottom**, and only source changes move
up. State this as the reason in the PR body, so it does not read as an arbitrary cut.

## Cutting an existing branch into two layers

The branch already holds the whole change. Cut it by subtraction, never by cherry-picking.

```bash
git fetch origin
MB=$(git merge-base origin/main origin/FEATURE)   # the merge-base, not origin/main
git tag -f split-baseline origin/FEATURE          # the "lose nothing" reference
git diff --no-renames --name-status "$MB"...split-baseline > /tmp/status.txt   # renames as D + A
```

Partition every path in `status.txt` into bottom and top. Materialise the top set to a file,
split by status, because `git checkout` treats each status differently:

```bash
awk -F'\t' '$1=="M"||$1=="T"{print $2}' top-set.txt > M-paths   # T = typechange
awk -F'\t' '$1=="D"{print $2}' top-set.txt > D-paths
awk -F'\t' '$1=="A"{print $2}' top-set.txt > A-paths
```

Build the **bottom** by restoring the top's paths to merge-base content:

```bash
git switch FEATURE
[ -s M-paths ] && git --literal-pathspecs checkout "$MB" --pathspec-from-file=M-paths
[ -s D-paths ] && git --literal-pathspecs checkout "$MB" --pathspec-from-file=D-paths   # re-creates deletions
[ -s A-paths ] && git --literal-pathspecs rm --pathspec-from-file=A-paths   # drops additions
git commit
```

Build the **top** by resetting onto the new bottom and re-applying from the baseline tag:

```bash
git switch -c TOP FEATURE
git reset --hard FEATURE
[ -s M-paths ] && git --literal-pathspecs checkout split-baseline --pathspec-from-file=M-paths
[ -s A-paths ] && git --literal-pathspecs checkout split-baseline --pathspec-from-file=A-paths
[ -s D-paths ] && git --literal-pathspecs rm --pathspec-from-file=D-paths   # re-applies deletions
git commit
```

Four things this shape exists to survive:

- **Restore from the merge-base, not the default branch tip.** A three-dot diff
  (`origin/main...FEATURE`) is taken from the merge-base, so merge-base content is what makes
  a path vanish from it. Restoring from the tip drags post-branch default-branch content onto
  your layer for any path that moved meanwhile.
- **`git checkout` cannot apply a deletion**, and errors on a pathspec absent from the ref.
  Every non-`M` status needs the explicit `git rm` or reverse-checkout above.
- **`--literal-pathspecs` on every checkout and rm.** Git globs pathspecs even from a file, so
  `app/[id]/page.tsx` also matches `app/i/page.tsx`. `--pathspec-from-file` keeps spaces intact,
  and the `[ -s ]` guard matters: an empty file turns `git checkout <ref>` into a branch switch.
- **Rebuild the top rather than rebasing it.** Resetting onto the new bottom and re-applying
  the file set is one clean commit; rebasing hundreds of commits through a subtraction is not.

## The bar

Run all five on the local branches before pushing, then re-run 1 to 3 on the pushed SHAs.

1. `git diff split-baseline TOP` is **empty**. The stack loses nothing: its top tree is
   byte-identical to the branch you started from.
2. `git diff --name-only origin/main...BOTTOM` contains no top-set path.
3. `git diff --name-only BOTTOM...TOP` is **exactly** the top set, no more and no less.
4. The two file counts sum to the original count.
5. `gh pr view <top> --json baseRefName` is the bottom branch. A top PR based on the default
   branch shows the entire original diff and defeats the exercise.

Bars 1 to 3 pin both trees completely: 1 fixes the top, 3 fixes where bottom and top differ,
2 fixes those paths on the bottom. Anything the original branch's CI already proved carries
over to the top for free, because bar 1 makes it the same tree.

Then assert **pushed equals verified**: `git rev-parse origin/BOTTOM origin/TOP` must match
the SHAs that passed. Review-fix commits pushed later restale every bar, so re-run them at
landing time.

## Landing the stack

The safe order is **merge down**: land the top into the bottom's branch, let the bottom PR run
the full suite on the combined change, then merge the bottom to the default branch as one
commit. Net effect on the default branch is identical to merging the original PR; only the
review experience changed.

Guard the bottom PR against an early merge for as long as the stack is open:

- Keep it a **draft**. Drafts still take reviews and comments, still run CI (`synchronize`
  fires on every push; `converted_to_draft` is not a trigger workflows listen for), keep
  existing approvals, and cannot have auto-merge enabled.
- Prefix the title, for example `[stacked 1/2, do not merge alone]`, and say why in the body.

Budget for one more approval round at the finish line. Undrafting re-requests CODEOWNERS
reviews that were deferred while the PR was a draft, and the merge-down push can dismiss
approvals gathered during review.

## `gh stack`

`gh extension install github/gh-stack`. Run `gh stack --help` for the command surface; only
the choices below are worth knowing in advance.

- `gh stack link` attaches existing PRs to each other as a stack on GitHub without taking over
  local branch tracking. This is the verb to use when the bottom PR already exists.
- `gh stack view` shows every branch, its PR, status, and latest commit.
- `gh stack init b1 b2` adopts existing branches into a tracked stack.
- `gh stack submit` **creates** PRs, so on an existing bottom PR it can open a second one
  rather than reuse it. Prefer `link`.
- `gh stack merge` merges the stack **bottom-first**, which is the opposite of the merge-down
  order above. Land the stack by hand.
