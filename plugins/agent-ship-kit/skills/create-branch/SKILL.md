---
name: create-branch
description: Create a git branch named `TICKET-ID/type/description`, or `type/description` without a ticket. Use when starting work on a ticket, or when a new feature, bug, spike, hotfix or release branch is needed. Recognizes ticket keys like ABC-123.
---

# Create Branch

## Naming

| Scenario | Format | Example |
|---|---|---|
| With ticket key | `TICKET-ID/type/description` | `ABC-123/feature/add-search` |
| Without | `type/description` | `feature/add-search` |

| What the change is | Type |
|---|---|
| New feature or behaviour | `feature` |
| Bug fix | `bug` |
| Urgent production fix | `hotfix` |
| Investigation, no code shipped | `spike` |
| Release branch | `release` |

## Workflow

The helper is `scripts/create-branch.sh` in this skill's base directory.

1. **Ticket key** from the request, pattern `[A-Z][A-Z0-9]+-[0-9]+`. None → no prefix.
2. **Type and description**, when not given: read `git diff --stat HEAD` (or `--staged`), pick the type from the table, and slug the change in kebab-case (`add-search-filter`). Ask only when the diff is empty or truly ambiguous.
3. **Create**: `bash <skill-dir>/scripts/create-branch.sh [TICKET_ID] <type> <description>`.
4. **Confirm** the branch and relay the PR title and commit reminders the script prints.

A repo whose own docs define a different branch convention wins over this one.
