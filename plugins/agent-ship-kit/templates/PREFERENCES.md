# Preferences (example)

Personal working preferences, separate from the house rules. These are examples: keep what
fits, replace the rest. Include from your global instructions the same way as `HOUSE-RULES.md`.

## Commands

- Don't start dev servers; assume one is running.
- Don't run builds unless asked. Prefer check commands: typecheck, lint, tests.

## Code style

- Prefer the simplest solution that works. If a simpler approach exists, propose it.
- No `any` in TypeScript unless there is no alternative.

## Comments

- Short: 2-4 lines, one idea, the non-obvious fact and its consequence. Omit when the code
  already says it.
- No `file:line` references into other code; line numbers drift and the reference rots.
- A long comment defending a workaround means the code is wrong. Fix the code.

## Git

- Decide on attribution once: whether agent co-author trailers or "generated with" footers go
  into commits and PRs. State it here so every session follows it.

## Reporting

- Be concise. Lead with the result, then what is left.
