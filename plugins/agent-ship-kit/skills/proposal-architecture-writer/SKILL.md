---
name: proposal-architecture-writer
description: Write proposals, architecture and design docs, RFCs, decision records, and migration game plans in a direct, evidence-first team voice. Use when drafting or revising a proposal, technical design, architecture doc, RFC, decision doc, or tech evaluation, or when a draft reads generic and needs its claims backed.
---

# Proposal and architecture writing

The voice here is not a set of phrases. **Claims are cashed out**: each one is followed by the mechanism and the numbers that make it undeniable. Reproduce that and the voice follows. Manufacture the surface moves without it and the doc reads like a template, however polished.

The drift this skill writes against: bulleted benefit lists and abstract harm ("introduces unnecessary complexity", "provides limited customer value") with no mechanism behind them.

## How the voice works

**Cash out the claim.** Do not assert that something is slow, expensive, or broken. Walk it: *filter after loading and a 20-hit page may yield two rows for this customer, or none, with real matches stranded further back.* *Every page view triggers a paid API request, so the cost recurs on every view and scales with traffic.* A small concrete scenario with real numbers does the persuading.

**Verified, not assumed.** Evidence sits inline: a count from the real system (for example, `N files import via the alias`, `0 use deep relative imports`), a live pilot URL, a ticket, a billing figure, a measured threshold. Where something was checked rather than reasoned, say so.

When you cannot verify anything (no repo access, no metrics, a problem handed over as prose), say so and let it change the ask. Name what the evidence actually is ("one Lighthouse run on one machine, not a baseline"), and make getting a baseline step one. Thin evidence is a finding. Writing the surface form of evidence (*we checked*, *already validated*, invented thresholds) over facts you do not have is the one failure that discredits the whole doc.

**Rule, then exhaustive mapping, then the exception.** State the convention, apply it to every real case in a table or list, then call out the one that does not fit and say what happens to it.

**Map ownership before mechanism.** When a change spans systems, one sentence assigning each concern to its system explains why an apparently simple feature is not simple. Then propose.

**Return to a mechanism as often as it earns it.** The same constraint may appear three times if each appearance adds a different failure. Layered explanation is not repetition.

## Sentence texture

Drafts go wrong here most often. Strong docs read short because their *bullets* are short; their **prose is long and causal**.

| Property | Bar |
|---|---|
| Prose sentence | Median 16 to 22 words. Long where a mechanism needs it |
| Bullets | Short. Terse fragments belong here |
| Paragraph | 2 to 4 sentences. Longer when one causal chain runs on; never chop a mechanism to hit a number |
| Doc length | Scale to the decision: ~400 to 600 words for a modest internal fix, 700 to 1,200 for a normal proposal, up to ~1,600 when implementation detail earns it |
| Headings | Roughly one per 100 words |

A prose median near 12 means the mechanism got broken into declaratives and the reasoning went with it.

- **Connective scaffolding** over aphorism: *The problem is that…*, *The important part is…*, *The challenge is…*, *This also compounds…*.
- **Person.** "We" throughout. "I" only in a doc that is explicitly an opinion.
- **Assertion.** Firm where verified: *requires*, *cannot*, *already built*, *does not*. Scope uncertainty with a boundary or dependency (*for now*, *until the search service indexes it*) rather than stacked hedges.
- **Bold liberally, mid-prose.** Aim for roughly 13 to 18 bold spans per 1,000 words, most inside prose rather than as scan labels. Bold the decision-driving figure where it sits, the named term a skimmer needs, and the clause carrying the finding. A skimmer should get the argument from the bold alone.
- **Arrows and outcome marks.** `→` for a requirement or lookup flow (*open account → search → relevant tasks*); ✅/❌ to contrast which cases work.
- **Contract naturally**: *it's*, *isn't*, *don't*.
- **Cite so a reader can check.** Name the artifact: the ticket (`ABC-123`), the pilot URL, the prior doc, the bill line. Decision docs usually close with a References list.
- **Identifiers** keep exact casing in backticks. `~` or a range for approximations. Annualise costs when the argument is about cost.

## Conditional moves

Each earns its place or stays out. Forcing one produces exactly the template this skill exists to avoid.

- **The ask**, for decision-seeking docs. Name what you want in the reader's power to grant, once, where they will act on it. An assessment can explain without asking; a decision doc without an ask has missed its point.
- **TL;DR**, near-universal. Use bold labels (**Cost**, **Fix**, **Status**, **Trade-off**, **Ask**) only when the bullets really are different drivers; otherwise plain bullets. Either way the direction of the answer is in it.
- **The corrective**, a short *X is not Y* line, only where a reader carries a wrong default and only next to the evidence that kills it: *this is a hard cliff, not a trim* lands because the measurement precedes it. No misconception, no corrective.
- **What we tried first**, only when an approach was genuinely attempted. What it achieved, the blocker, the takeaway. A closed door is the strongest argument for the proposed one.
- **The admitted cost**, stated once, plainly, where it is most load-bearing: *we lose the custom export format; everything else is unchanged.* Repeating it reads as anxiety, not candour.
- **Alternatives**, only where someone could reasonably choose one. Each keeps the circumstance where it would win and gets a specific failure mode. Where none is credible, say so in a line.
- **Concern table**, when several objections were reviewed and came back fine. Each row names what was checked; a row you cannot source does not belong.

## Reuse the move, not the wording

These strings are crutches; perform the move in your own words: *What we tried first:* · *The takeaway:* · *came back fine* · *What we need from you:* · *the alternatives are exhausted* · *This isn't theoretical*. A draft reproducing three or four of them is a pastiche.

Hold antithesis to one or two constructions per doc, functional rather than epigrammatic. *The index finds records; it is not the authorization boundary* earns its place. *A correctness concern rather than a nicety* is essayist diction.

**The evidence gap as the finding.** When nobody has measured it, name what the evidence actually is, make measuring step one, and let the ask become baseline-then-build.

**Validation over KPIs.** Show it working (a live pilot, or a monitoring item naming the signal: *watch the nightly job failures drop to zero*) rather than a block of invented targets.

## Writing it

1. **Establish the problem first.** Read the code, ticket, dashboard, or bill and get real figures. Infer what you can reach rather than returning a questionnaire; ask the human only where the answer changes the recommendation.
2. **Order the spine as claims with their evidence.** Problem → what exists → what breaks → proposal → bounded first iteration → cost → ask, taking only the parts this problem has. Mark evidence gaps as assumptions beside the step they affect.
3. **Pick sections** from [`references/patterns.md`](references/patterns.md) (section menu, doc-type skeletons, option block, rollout pattern). For a system rather than a single decision, also read [`references/architecture.md`](references/architecture.md).
4. **Draft**, prose causal and bullets terse.
5. **Run the gate.** Optionally pair with a de-AI editing pass (for example the third-party `humanizer` skill) after the gate passes.

## The gate

1. Every load-bearing claim is cashed out (a mechanism, a count, a scenario) and nothing asserts evidence you do not have.
2. Prose reads at full causal length, the short lines living in bullets. Measure rather than trust it, from the doc's directory:
   `python3 -c "import re,statistics,sys;t=re.sub(r'^\s*[-*|#].*$','',open(sys.argv[1]).read(),flags=re.M);l=[len(s.split()) for s in re.split(r'(?<=[.!?])\s+',t) if len(s.split())>3];print('prose median',statistics.median(l))" DOC.md`
3. Each move present earns its place: the corrective sits next to its evidence, the failed attempt really happened, the alternatives are ones someone would pick.
4. The admitted cost appears once.
5. Where a decision is wanted, the ask is in the opening block and names something grantable.
6. Assumptions and material risks each have containment, an owner, or a validation path.
7. Section count matches the decision's weight (four or five for a modest fix), and no section exists because a skeleton listed it.
8. None of the crutch strings appear.
9. Bold density sits near 13 to 18 per 1,000 words, with decision-driving figures bolded in prose.
10. Every figure names the artifact a reader could check, or is written as a labelled assumption.
