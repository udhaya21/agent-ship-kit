# House rules: invariants that gate shipping

Standing rules that hold no matter how a goal is reached. An underspecified goal is safe only
because these fence it. When a rule conflicts with speed or convenience, the rule wins.

Copy this file next to your global agent instructions (for example `~/.claude/HOUSE-RULES.md`,
included from `CLAUDE.md` with `@HOUSE-RULES.md`, or pasted into `AGENTS.md`) and edit the
model names to match the models you actually have.

## The rules

1. **No delegation without a bar.** Every piece of delegated work carries a concrete pass/fail
   test declared before the build. Adjectives ("high quality", "clean", "polished") are not bars.
2. **The builder never grades its own work.** Grading goes to a different model, in a fresh
   context, pointed at the real output (pixels, running app, diff), told to prove FAIL.
3. **No hard-coded special cases in agent behavior.** When building agents or prompts, describe
   the desired behavior and let the model reason. Don't bolt on regex filters or if-chains for
   individual cases.
4. **Taste-critical output comes from your strongest model.** UI, copy and API design are not
   handed to a cheaper or faster model to save cost.
5. **One model by default.** Delegate only for parallel work, digest-only analysis, or
   independent review (see the `delegation-rules` skill).
6. **Report reality.** Failing tests, skipped steps and unverified claims are stated plainly.
   No rounding up to "done".
7. **Nothing sensitive leaves the machine.** External services get progress notes and
   screenshots, never secrets, credentials or proprietary source.

## The gate

Before any commit or push, a rule-check reviewer (a different model than the one that wrote the
change, high effort, fresh context) checks the diff against the rules above and the declared bar.
It returns PASS or a list of violations. Violations block the push until fixed or explicitly
waived by a human.
