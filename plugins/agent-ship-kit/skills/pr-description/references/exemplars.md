# Exemplars

Illustrative bodies showing the target shape. They use the fallback skeleton; a repo template or the repo's own history replaces it. The scenarios are invented.

## Fix: symptom → root cause → fix

```markdown
Ticket: ABC-231

## Description of changes

- Previously, the CSV export showed totals one cent off for some invoices (`10.01` instead of `10.02`).
- The cause was `formatAmount` summing floating-point line totals and rounding once at the end.
- Switched to summing integer cents and formatting once, so every row and the total round the same way.

## How to test

- Export an invoice with three lines of `3.34`.
- Confirm the total reads `10.02` in the CSV and on screen.
- Verify single-line invoices are unchanged.
```

## Feature: bold-label bullets

```markdown
Ticket: ABC-380

## Description of changes

- **Why:** Users asked to keep their place in long lists after opening a detail page.
- **How:** New `useScrollRestore` hook stores the list's scroll offset per route and restores it on back navigation.
- **Rollout:** Behind the `scroll-restore` feature flag, off by default.
- **Trade-offs:** Offsets are kept in memory only, so a full reload starts at the top.

> [!NOTE]
> Infinite-scroll lists restore only the pages already loaded. Loading earlier pages on restore is tracked in ABC-391.

## How to test

- With the flag on, scroll a long list, open an item, go back, and confirm the position is kept.
- With the flag off, confirm the list opens at the top as before.

| Before | After |
| --- | --- |
| _screenshot_ | _screenshot_ |
```

## Chore: two concerns, two bullets

```markdown
Ticket: ABC-207

## Description of changes

- Upgraded Node from 20 to 22 in CI, `.nvmrc` and `engines`.
- Removed the `node-fetch` polyfill, now that the runtime ships `fetch`.

## How to test

- Run a clean install and the test suite on Node 22 and confirm both pass.
```
