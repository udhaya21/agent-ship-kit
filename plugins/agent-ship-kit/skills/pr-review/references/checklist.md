# Review checklist

Reached from [SKILL.md](../SKILL.md) step 2. Sections are stack-agnostic unless labelled. Labelled sections (React, TypeScript, Next.js, Tailwind) apply only when the diff uses that stack. A repo overlay overrides anything here.

## Always check

Roughly in order of how often each fires:

1. **Duplication**: logic repeated across call sites; extract a shared helper, hook, or component.
2. **Naming**: vague or generic identifiers, names gone stale after a refactor, booleans without an `is`/`has` prefix.
3. **Dead weight**: unused imports, variables, and exports; commented-out code; leftover debug logging or markup; guards for conditions an earlier step already guarantees.
4. **Missing tests**: raise only when you can name the one specific untested case that would plausibly break (the branch, the boundary value, the error path). A generic "add tests?" or an enumerated scenario matrix names nothing the author did not know.
5. **Missing why-comments**: non-obvious conditional, business, or workaround logic with no statement of intent.
6. **Hardcoded user-facing strings** that bypass the translation layer.
7. **Cross-flow blast radius** (blocking): a change to shared code verified only in the reported flow. Check every consumer, viewport, and code path it touches.
8. **Silent placeholder fallbacks** (blocking): `?? ''` or `?? 0` for a missing critical value passes types and ships invalid data. Throw, or use a genuinely valid fallback.
9. **Error-handling hygiene**: environment-dependent operations (storage, parsing, I/O) unguarded; caught errors swallowed instead of reported; generic error names; a missing `await` inside try/catch.
10. **Type precision**: escape hatches (`any`, forcing casts, suppression comments), truthy checks where valid falsy values exist, `||` where `??` is meant, hand-written types duplicating a canonical source.
11. **Accessibility**: see the section below for any UI change.
12. **Security** (blocking): see the section below.
13. **PR hygiene**: scope creep, unexplained formatting or lockfile churn, TODOs without a ticket, stray files.
14. **Gated work with global side effects**: when a feature sits behind a flag, every app-wide side effect it adds (global CSS, meta tags, a hook mounted at the root, polling, storage writes) must be gated by the same flag or be harmless with it off. Check the global mount points, not only the feature's files.

## Accessibility

- ARIA roles and attributes match the spec for the actual widget pattern, placed on the focusable element whose role supports them, not on a wrapper.
- Use the native element for the job: an anchor for navigation, a button for actions, real lists for genuine item sets.
- Every icon-only or ambiguous control has a descriptive accessible name; alt text describes the real content or is empty for decoration.
- Focus is managed deliberately and indicators stay visible, including in forced-colors mode.
- Heading levels follow real hierarchy.
- Relationship and live-region attributes point at permanently mounted elements; avoid re-announcing state mid-interaction.
- Omit optional ARIA attributes (undefined) when there is nothing to announce, rather than empty string or false.
- No interactive or block content nested inside a button or large clickable area.
- Grouped controls use fieldset/legend or a radiogroup.
- Anything mouse-operable, including click-outside dismissal, is keyboard-operable.
- Colour is not the only signal (keep link underlines at rest).
- Prefer `aria-disabled` when the control must stay focusable.

## API design

- Keep public surface minimal; add props and exports when genuinely needed.
- Fetch or expose only fields that are consumed.
- Make a field required only when every caller can supply it; nullable whenever it can legitimately be missing or its resolver can fail.
- Removing or renaming a public element is breaking; deprecate first.
- Keep names and capabilities consistent across sibling components.
- Model success and failure responses as a discriminated union, not one ambiguous shape.
- More than two related parameters: accept an options object.
- When replacing an integration, call out behaviour differences explicitly.

## Simplification

- Early-return guard clauses over nested conditionals.
- Named constants for repeated magic values; one source of truth for config.
- Simplify boolean expressions; no double negation.
- Reuse an existing utility before writing a new one; question any new abstraction that is not earning its keep.
- Do not pass a value that matches the default.
- Duplicate implementations of the same check must stay consistent, or become one helper.

## Comments and docs

- Explain the why behind non-obvious logic; delete comments that restate the code.
- Keep comments and docs in sync with the code; remove stale ones.
- Every TODO carries a ticket, and goes when the work is done.
- Comments stand alone without the PR description.
- Use the specific doc tag for special status (deprecated, internal).

## Error handling

- Specific, named error classes for known failures; preserve the original as `cause` when rethrowing.
- Attach diagnostic identifiers (failure reason, entity id, subsystem) to captured errors.
- Match severity to reality: real failures go to the error tracker; expected conditions get plain logging.
- Error messages name the actual failed precondition, not a copy-pasted one.
- Distinguish "still loading" from "genuinely invalid" before throwing or redirecting.
- Validate required env vars and config at startup; fail fast.
- After handling an error, return; do not fall through to the success path.
- Isolate best-effort work so its failure cannot gate the primary flow, and vice versa.
- Return the status-appropriate error (400, 404) rather than a generic 500.
- An unhandled branch of a switch or if-else must not silently return undefined.
- When control flow changes, confirm no necessary branch became unreachable.

## Security

- Client-controlled headers, query params, and referrers are not identity.
- A resource fetched by a client-supplied id is checked against the requesting tenant or user (IDOR).
- Redact tokens, full URLs with query strings, and client IPs before logging or forwarding.
- Validate hostnames against an explicit allowlist with exact or suffix matching, in every code path, never substring.
- No secrets or credentials in source, including tests.
- Guards fail closed: an unset config or a non-throwing failure branch must not allow access.
- Payment or quota enforcement has no bypass through special-case code or client-supplied values.
- An intentionally unauthenticated path documents its trust model.

## Testing

- Assertions check the exact expected condition, not a loose format or partial match.
- Shared setup (locators, fixtures, boilerplate assertions) lives in helpers.
- New or changed user-facing, error, or money-affecting flows get end-to-end coverage.
- E2E selectors use test ids, roles, or text, not utility classes or positional selectors.
- Tests are deterministic: pin dates, timezones, and locales.
- Re-derive a changed snapshot or expected value before accepting it.
- Confirm a mock actually attaches to the code under test.
- Question unexplained changes to test or CI configuration.

## i18n

- User-facing strings go through the translation function; reuse existing keys.
- Use logical CSS properties (inline-start, inline-end) for RTL.
- Use `Intl` for locale-aware formatting; handle currencies without minor units.
- Flag locale-dependent behaviour explicitly.

## Performance

- Import from specific modules rather than barrels where tree-shaking matters.
- Hoist computations that do not depend on input to module scope.
- Scope each route's data query to what that route needs.
- Keep fast-changing state low in the tree.

## React (when the diff uses React)

- Derive state with plain computation or `useMemo` instead of syncing it through an effect.
- No fresh objects or arrays in dependency arrays; extract stable primitives.
- Browser-only APIs stay out of render; guard them behind an effect or an isomorphic hook.
- Effects that set up listeners or timers return a cleanup.
- No side effects in render or inside `useMemo`.
- A `useState` plus `useEffect` pair mirroring a browser API (online status, media queries, visibility) is usually a reinvented `useSyncExternalStore`.
- Use `useId()` for DOM ids in server-rendered components, never `Math.random()`.
- Prefer a callback ref over effect plus `ref.current` for imperative DOM actions.
- Render components as JSX, never by calling them as functions; never use `key` as a remount hack.
- Use the functional `setState` updater when the next value depends on the previous.
- Gate every path that exposes a feature on its complete precondition.
- Check an ancestor does not already supply a context before adding a provider.
- Keep presentational components free of business logic.

## TypeScript (when the diff uses TypeScript)

- Fix the error rather than suppress it; if unavoidable, `@ts-expect-error` with a reason.
- No `any`; no `as` assertion forcing a mismatched value past the checker.
- Derive types from their canonical source.
- Check the precise null or undefined condition the type allows.
- Use `as const` or `satisfies` to keep literal types.
- Model mutually exclusive shapes as a discriminated union.
- Make a field required when it should never be absent.
- When adding a union or enum variant, confirm every exhaustive switch handles it.
- Type-only imports for types; strict equality everywhere.
- Drop redundant optional chaining for values the type guarantees.

## Next.js (when the diff uses Next.js)

- Keep app-wide wrappers (`_app`, root layout) for truly site-wide concerns.
- Reserve 404 for genuine not-found; route real errors to the error page.
- No `'use client'` where it has no effect.
- New redirects follow the routing conventions already established for that flow.

## Styling with Tailwind (when the diff uses Tailwind)

- Verify every utility class exists; invented or mistyped classes silently do nothing.
- Remove classes that restate a default or are overridden elsewhere.
- Prefer scale-mapped utilities over arbitrary values when one matches; reference tokens rather than raw values.
- Prefer logical-property utilities for RTL.
