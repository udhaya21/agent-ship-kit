# Section patterns

Reached from [`SKILL.md`](../SKILL.md) step 3.

## Section menu

Pick what the problem needs. Six to nine sections suit a cross-team or costly change; four or five suit a modest one.

**Load-bearing in nearly every doc**
- **TL;DR**: bullets with the recommendation inside
- **Problem / Context**: observable failure modes
- **Current state**: what exists, what is worth keeping
- **Proposal**: the mechanism, concretely
- **Trade-off**: the admitted cost
- **Recommendation / Ask**: what you want granted

**Situational, only when the problem calls for it**
- **What we tried first**: a real prior attempt and the blocker that killed it
- **Validation**: a pilot, a measured result, a live URL
- **How others organise this**: prior art, with sibling projects in your own org as the strongest signal
- **Cost impact**: a table when cost drives the decision
- **Customer experience**: when the cheaper path is also the better one
- **What needs to change**: the gap between reuse and requirement
- **Decisions (confirmed)**: settled points, so review does not relitigate them
- **Alternatives considered**: only where a real choice exists
- **Iteration 1 / scope boundary**: what this does not cover
- **Rollout / Migration**: see the rollout pattern below
- **Observability / success checks**: how you will know it worked
- **Open questions**: a real question someone must answer, each with a named owner
- **References**: tickets, docs, sources, superseded docs

**Leave out**: a separate Executive Summary (the TL;DR is it), Glossary, Best Practices, a Conclusion that restates, generic pros/cons matrices detached from the decision, and an Assumptions section collecting what belongs beside each step.

## Skeletons by doc type

Titles signal maturity, so pick the prefix deliberately: `Proposal:` seeks agreement, `Decision Proposal:` seeks a yes/no, `Game Plan:` assumes the direction and coordinates execution, `Thoughts on` is an opinion, an unprefixed noun phrase reads as an assessment.

**Cost or vendor-change proposal**
TL;DR → Background with the cost trend → What we tried first and why it failed → Proposed solution → Validation on a pilot → Cost impact table → Customer experience → Trade-off → Recommendation with the ask and remaining steps → References

**Capability or feasibility assessment**
TL;DR → Ownership mapping across systems → What we already have → What needs to change → Other work required → The blocking limitation → Proposed approach → Iteration 1 scope → What is deferred → Trade-off → Recommendation

**Scoped refactor proposal**
Scope banner and no-behaviour-change note → TL;DR → Verified-against-the-code evidence box → Context and problem → How others organise this → Decisions (confirmed) → Target structure → Mapping table → Conventions → References

**Decision proposal**
TL;DR ending in the recommendation → Background → Current problem with a customer ticket → Recommendation with reasoning → Proposed decision. Where the decision is already settled, lead with it before any context.

**Migration game plan**
Objective with the customer-safety invariant → Current setup → Proposed setup → Team responsibilities and owners → Preparation → Switchover with dated increments → Post-switchover checks → Open questions

**Technology evaluation**
TL;DR with the corrective up front → Background → How it fits in → Migration scope → Proposed approach → Caveats → Recommendation

## The option block

Each option gets the same shape, so options stay comparable:

```
### Option N: <name>
Complexity: Simple | Moderate | Complex
Effort: <estimate or range>

<mechanism in two or three sentences>

Pros: <what it genuinely buys>
Cons: <the specific failure mode or cost>
```

Close with a recommendation that may be conditional: *worth doing if account-level filtering lands in the search service; not otherwise.* A rejected option keeps the circumstance under which it would win.

## The rollout pattern

Take the steps the change actually needs:

1. State the non-negotiable customer guarantee: no customer notices this.
2. Name owners by team, and the release and QA owners by person.
3. Pre-flight checks: env vars set across environments, flags in place, key restrictions verified.
4. Route a small weighted share to the new path, keeping fixed cohorts on both old and new.
5. Validate: functionality, analytics, error rates, logs, scaling behaviour.
6. Increase traffic on dated steps.
7. Keep the old path alive and observed; rollback is a revert, not a rebuild.
8. Migrate stateful dependencies once traffic is stable.
9. Decommission after an explicit stability window, and name what gets deleted: the handler, the signing secret, the rate limiter.

Rollback safety is architectural, not a reassuring sentence: incremental routing limits blast radius, dual cohorts keep both paths testable, delayed teardown preserves reversibility.

## Structural craft

Transferable reasoning, not wording:

- Separate hard requirements from the performance bar you set yourselves.
- Trace a defect through the current workflow rather than listing complaints.
- State the durable invariant that decides which controls matter, then let the recommendation follow from it.
- Describe normal, degraded, and exceptional flows separately.
- Put trade-offs after demonstrated value and before next steps.
- Pair every admitted liability with containment or a validation path.
- Assign owners to outcomes, not just to tasks.
- Mark the step that depends on a spike, at that step.
- End an exploratory doc on the questions needed to close it.
- Define success as a before/after measure or a scheduled check.
