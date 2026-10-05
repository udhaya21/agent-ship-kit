#!/bin/bash
# Usage:
#   commit.sh --fix-only                                lint + format staged files, re-stage
#   commit.sh <type> "<scope|>" "<message>" [TICKET_ID] commit the index as-is, conventional format
set -e
# Treat file names as literal paths, never as pathspec patterns.
export GIT_LITERAL_PATHSPECS=1

fix_staged() {
  local files=() lint=() f
  while IFS= read -r -d '' f; do files+=("$f"); done \
    < <(git diff --staged --name-only --diff-filter=ACMR -z)
  if [[ ${#files[@]} -eq 0 ]]; then
    echo "No staged files to fix."
    return
  fi
  # Re-staging a partially staged file would pull its unstaged edits into the commit.
  if [[ -n "$(git diff --name-only -- "${files[@]}")" ]]; then
    echo "Skipping lint/format: some staged files also have unstaged changes." >&2
    return
  fi
  for f in "${files[@]}"; do
    [[ "$f" =~ \.(js|ts|jsx|tsx|mjs|cjs)$ ]] && lint+=("$f")
  done

  if [[ -x node_modules/.bin/prettier ]]; then
    echo "Running prettier on staged files..."
    node_modules/.bin/prettier --cache --write --ignore-unknown -- "${files[@]}"
  fi
  if [[ ${#lint[@]} -gt 0 && -x node_modules/.bin/eslint ]]; then
    echo "Running eslint --fix on staged files..."
    node_modules/.bin/eslint --fix -- "${lint[@]}"
  fi

  git add -- "${files[@]}"
  echo "Format complete. Files re-staged."
}

if [[ "$1" == "--fix-only" ]]; then
  fix_staged
  exit 0
fi

TYPE="$1"
SCOPE="$2"
MESSAGE="$3"
TICKET_ID="$4"

if [[ ! "$TYPE" =~ ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)$ ]]; then
  echo "Error: type must be one of: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert" >&2
  exit 1
fi
if [[ -z "$MESSAGE" ]]; then
  echo "Error: commit message is required" >&2
  exit 1
fi

if [[ -z "$TICKET_ID" ]]; then
  BRANCH=$(git branch --show-current 2>/dev/null || echo "")
  if [[ "$BRANCH" =~ ^([A-Z][A-Z0-9]+-[0-9]+)/ ]]; then
    TICKET_ID="${BASH_REMATCH[1]}"
    echo "Inferred ticket key from branch: $TICKET_ID"
  fi
fi

if [[ -n "$SCOPE" ]]; then PREFIX="${TYPE}(${SCOPE}):"; else PREFIX="${TYPE}:"; fi
if [[ -n "$TICKET_ID" ]]; then FULL_MESSAGE="${PREFIX} ${MESSAGE} ${TICKET_ID}"; else FULL_MESSAGE="${PREFIX} ${MESSAGE}"; fi

echo "Committing: $FULL_MESSAGE"
git commit -m "$FULL_MESSAGE"
