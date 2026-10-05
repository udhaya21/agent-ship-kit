# agent-ship-kit

Skills and hooks for shipping code with coding agents: declare a pass/fail bar before
delegating, have a different model review the work, follow one convention for branches,
commits and PRs, split big PRs into stacks, and run a rule-check gate before every push.

The skills use the open [Agent Skills](https://agentskills.io/specification) format, so they
work in Claude Code, Codex CLI, OpenCode, Antigravity, Gemini CLI, Cursor, Copilot and Grok.
The hooks are Claude Code only. See [docs/providers.md](docs/providers.md) for where each tool
loads skills from, with links to each tool's skill-authoring docs.

## Install

**Claude Code** (skills and hooks):

```
/plugin marketplace add udhaya21/agent-ship-kit
/plugin install agent-ship-kit@agent-ship-kit
```

**Codex CLI** (skills):

```
codex plugin marketplace add udhaya21/agent-ship-kit
codex plugin add agent-ship-kit@agent-ship-kit
```

**Any agent**, through the [`skills` CLI](https://skills.sh):

```
npx skills add udhaya21/agent-ship-kit
```

**Tools that read `AGENTS.md`**: copy [`AGENTS.md`](AGENTS.md) into your project root. It carries
the house rules and an index of the skills.

Then copy [`templates/HOUSE-RULES.md`](plugins/agent-ship-kit/templates/HOUSE-RULES.md) next to
your global agent instructions and edit the model names to match the models you have.
[`templates/PREFERENCES.md`](plugins/agent-ship-kit/templates/PREFERENCES.md) is an example of
personal preferences kept separate from the rules.

## Skills

| Skill | What it does |
| --- | --- |
| `delegation-rules` | When to hand work to another agent or model, the pass/fail bar, kickoff package, bounding long runs, context budget |
| `codex-mechanics` | Driving Codex CLI from another agent without silent failures |
| `codex-review` | Independent Codex review of a diff, branch, commit or PR |
| `codex-computer-use` | Codex verifies a running app, browser flow or simulator |
| `create-branch` | `TICKET-ID/type/description` branch names |
| `commit` | Conventional Commits with the ticket key |
| `stacked-prs` | Split an oversized PR into a stack of reviewable layers |
| `pr-description` | PR title and body from the real diff and the repo's template |
| `pr-review` | Self-review before raising a PR, or draft comments on someone else's |
| `pr-review-and-approve` | Review end to end and post approve or request changes |
| `pr-visual-snaps` | Before/after screenshots of two deployed URLs, as a table in the PR |
| `proposal-architecture-writer` | Proposals, design docs, RFCs and decision records |

`pr-review` ships a stack-agnostic checklist. Add your team's own rules in a `REVIEW.md` at
the root of the repo being reviewed.

## Hooks (Claude Code)

| Hook | Default | What it does |
| --- | --- | --- |
| `orchestration-card` | on | On each non-trivial prompt, injects a short card: declare a bar, delegate only for a reason, bound every delegation |
| `context-guard` | on | Warns once when context passes the handoff threshold (200k) and once at the hard stop (300k) |
| `lsp-first` | off | Blocks bare camelCase/PascalCase grep over source files and points to the LSP tool. Turn on only with an LSP plugin installed |

Toggle them and set the thresholds in the plugin's options (`/plugin`, or
`claude plugin configure agent-ship-kit`).

## Requirements

`git` and the GitHub CLI `gh` for the branch, commit and PR skills; Node for `pr-visual-snaps`;
[Codex CLI](https://github.com/openai/codex) for the `codex-*` skills; Python 3 for the hooks.

## Pairs well with

Not included here; install them from their authors:
[Matt Pocock's skills](https://github.com/mattpocock/skills),
[humanizer](https://github.com/blader/humanizer), and the
[Codex plugin for Claude Code](https://github.com/openai/codex-plugin-cc).

## Credits

The delegation rules build on [Theo's](https://x.com/theo/status/2072482460122964067?s=46)
rate-limit thread and Matt Shumer's
["How I Prompt Fable"](https://simplemarkdowneditor.com/pub/IbaCrTjLJT?key=uQOQ2NPO3TTUSXyYDjyLf).

## License

MIT. See [LICENSE](LICENSE).
