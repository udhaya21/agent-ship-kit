# Architecture and design docs

Reached from [`SKILL.md`](../SKILL.md) step 3 when the doc describes a system rather than requesting a single decision. The voice bars and the gate in `SKILL.md` still apply.

Architecture docs are rarely written from complete information. The job is to turn partial context into a document an engineer can build from and a reviewer can argue with, not to wait for the full picture.

## Turning thin context into a design doc

Work in this order. Each step is answerable from the code, the tickets, and the systems you can reach; where it is not, it becomes a labelled assumption rather than a blocker.

1. **Name the systems and who owns what.** One sentence assigning each concern to a system is worth a page of prose: *the catalog service owns book records, the loans service owns checkouts and due dates, the members service owns members and the search the catalog queries.* This tells the reader why an apparently simple feature spans three teams.
2. **Draw the boundary of the change.** What is inside this design, what stays untouched, and what belongs to another team. State the dependency you need from them explicitly: *this needs `homeBranch` in the members index, exposed as a search filter*.
3. **Trace the flow end to end**, numbered, in the order a request travels. Name the hop that is slow, paid, or fragile. Where fetches must be sequential, say why.
4. **Give each component its responsibility in one line**, then its interactions. A responsibility the reader can restate beats a box diagram.
5. **Describe the states separately.** Normal, degraded, and exceptional paths each get their own description: hit, stale, and miss are three behaviours, not one cache.
6. **Take the failure modes one at a time.** Trigger, observable symptom, containment. Stale index entries, partially filled pages, an upstream that takes 2s for the largest catalogs: these are the parts worth writing down.
7. **State the architectural decisions as decisions**, reasoning attached, so review does not relitigate them. Include the ones that constrain the design: *the index finds records; it is not the authorization boundary.*
8. **Bound the first iteration.** What Iteration 1 delivers, what it explicitly does not, and what is deferred to a separate problem.

## Non-functional concerns

Weave these into the component or flow they affect. Give one its own section only when it drives the design.

- **Scalability**: name the thing that grows and what grows with it (per-view cost scaling with traffic, rebuild cost scaling with page count, fan-out per account).
- **Reliability**: the authoritative source, and what happens when the derived copy is stale. Post-load validation against the real record is a common pattern.
- **Security**: the authorization boundary and where it is enforced. Note deliberately safe exposures and why (a referrer-restricted key in an embed URL is safe by design). When the design touches authorization, tenancy, or key handling, cover it properly; it is the concern drafts most often under-treat.
- **Observability**: what you will watch to know it worked (a cost line going to zero, p90 latency, error rates, cache hit rate). Name the signal, not "we will add monitoring".
- **Cost**: annualised, tied to traffic, before and after side by side.

## Delivering the detail

- **Tables** for repeated-field comparison: from/to mappings, environment matrices, concern and assessment, cost before and after.
- **Diagrams** for routing and multi-system sequences. Without one, a numbered flow or a plain ASCII latency ladder carries it (an 800ms waterfall accumulating hop by hop).
- **Code and file trees** only when the structure is itself the proposal.
- **Concrete examples** over abstract description: a real URL, a real redirect, a real request.
- **Exact casing** in backticks for every path, flag, field, and API name.

## Migration inside a design doc

Where the design replaces something live, the rollout pattern in [`patterns.md`](patterns.md#the-rollout-pattern) applies. Two points matter most: what the reader can assume never breaks, and what gets decommissioned once the new path is stable. Naming the machinery you get to delete (a proxy handler, a signing secret, a rate limiter) is part of the argument for the change.
