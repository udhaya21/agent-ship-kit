#!/bin/bash
# Usage: create-branch.sh [TICKET_ID] <type> <description>
# TICKET_ID is optional. Without it the branch is type/description.
set -e

if [[ "$1" =~ ^[A-Z][A-Z0-9]+-[0-9]+$ ]]; then
  TICKET_ID="$1"; TYPE="$2"; DESC="$3"
else
  TICKET_ID=""; TYPE="$1"; DESC="$2"
fi

if [[ ! "$TYPE" =~ ^(feature|hotfix|bug|spike|release)$ ]]; then
  echo "Error: type must be one of: feature, hotfix, bug, spike, release" >&2
  exit 1
fi
if [[ -z "$DESC" ]]; then
  echo "Error: description is required (kebab-case, e.g. add-search-filter)" >&2
  exit 1
fi

if [[ -n "$TICKET_ID" ]]; then BRANCH="${TICKET_ID}/${TYPE}/${DESC}"; else BRANCH="${TYPE}/${DESC}"; fi

echo "Creating branch: $BRANCH"
git checkout -b "$BRANCH"

echo ""
echo "--- Reminders ---"
if [[ -n "$TICKET_ID" ]]; then
  echo "PR title:  ${TICKET_ID} - Your descriptive PR title"
  echo "Commit:    feat: your message ${TICKET_ID}"
else
  echo "PR title:  Your descriptive PR title"
  echo "Commit:    feat: your message"
fi
echo "Commit types: build | chore | ci | docs | feat | fix | perf | refactor | revert | style | test"
