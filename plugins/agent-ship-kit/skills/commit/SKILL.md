---
name: commit
description: Create a git commit in Conventional Commit format, with a ticket key when one applies. Use when committing staged work, or when the commit message format itself is the question. Picks the type and message from the staged diff and the ticket key (ABC-123 style) from the branch or request.
---

# Commit

Commit staged changes as `type(scope): message TICKET-ID`.

## Message format

```
type(scope): message TICKET-ID
```

- `type`: from the diff, by the table below.
- `(scope)`: optional, the primary module touched. Omit when changes span many areas.
- `message`: one concise sentence on *what* changed.
- `TICKET-ID`: optional, a key matching `[A-Z][A-Z0-9]+-[0-9]+` from the request or the branch.

| What the diff shows | Type |
|---|---|
| New feature or behaviour | `feat` |
| Bug fix | `fix` |
| Only `.md` or comment changes | `docs` |
| Formatting, no logic change | `style` |
| Restructure, same behaviour | `refactor` |
| Performance improvement | `perf` |
| Tests added or changed | `test` |
| Build config, bundler, deps | `build` |
| CI pipeline files | `ci` |
| Tooling, scripts, non-app config | `chore` |
| Reverting a prior commit | `revert` |

## Workflow

The helper is `scripts/commit.sh` in this skill's base directory.

1. **Check staged changes**: `git diff --staged --stat`. Nothing staged → show `git status --short`, ask "Stage all and commit?"; yes stages all modified tracked files, no asks which files.
2. **Format staged files**: `bash <skill-dir>/scripts/commit.sh --fix-only`. Runs the repo-local prettier and eslint `--fix` (from `node_modules/.bin`) on staged files when installed, then re-stages. It skips this step when a staged file also has unstaged edits, and a formatter or lint failure stops the commit.
3. **Pick** `type`, `scope` and `message` from the staged diff.
4. **Ticket key**: from the request, else the branch (`git branch --show-current`; `ABC-123/feature/...` → `ABC-123`). None found → commit without one.
5. **Commit**: `bash <skill-dir>/scripts/commit.sh <type> "<scope|>" "<message>" [TICKET_ID]`.
6. **Confirm** the hash and final message.

Ambiguous type → pick the best fit and say why. The message is the conventional line only: no attribution trailers.

## Examples

```
feat(search): add date range filter ABC-123
fix(auth): resolve token expiry on refresh ABC-456
refactor: simplify runtime config types
chore: update CI cache keys
```
