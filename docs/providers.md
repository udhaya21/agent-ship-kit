# Skills across agent tools

Every skill in this kit is a plain [Agent Skills](https://agentskills.io/specification) folder: a
`SKILL.md` with `name` and `description` frontmatter, plus optional `references/` and `scripts/`.
Most coding agents now load that format, but each one looks in different directories and
accepts different extra fields. This page collects where each tool documents skill authoring,
so you can adapt or write skills for the tool you use.

Checked against each tool's docs on 2026-10-05. Tools move fast; the linked docs win over this
page. "Unverified" means the official docs did not say.

## Where each tool looks

| Tool | Authoring docs | Project skills | User skills | Install from GitHub |
| --- | --- | --- | --- | --- |
| Agent Skills spec | [specification](https://agentskills.io/specification) | n/a | n/a | n/a |
| Claude Code | [skills](https://code.claude.com/docs/en/skills), [plugins](https://code.claude.com/docs/en/discover-plugins) | `.claude/skills/` | `~/.claude/skills/` | `/plugin marketplace add owner/repo` |
| OpenAI Codex CLI | [build skills](https://learn.chatgpt.com/docs/build-skills), [build plugins](https://developers.openai.com/codex/plugins/build) | `.agents/skills/` | `~/.agents/skills/` | `codex plugin marketplace add owner/repo` |
| OpenCode | [skills](https://opencode.ai/docs/skills/), [plugins](https://opencode.ai/docs/plugins/) | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | No GitHub command; plugins are npm packages |
| Google Antigravity | [skills](https://antigravity.google/docs/skills), [plugins](https://antigravity.google/docs/plugins) | `.agents/skills/` | IDE `~/.gemini/config/skills/`, CLI `~/.gemini/antigravity-cli/skills/` | `agy plugin install <plugin>@<marketplace>` (GitHub source unverified) |
| Grok Build (xAI) | [skills, plugins, marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces) | `.grok/skills/` | `~/.grok/skills/`, `~/.agents/skills/` | `/plugins` in the TUI |
| grok-cli (community) | [README](https://github.com/superagent-ai/grok-cli) | `.agents/skills/` | `~/.agents/skills/` | Unverified |
| Gemini CLI | [skills](https://geminicli.com/docs/cli/skills/) | `.gemini/skills/`, `.agents/skills/` | `~/.gemini/skills/`, `~/.agents/skills/` | `gemini skills install <git-url>` |
| Cursor | [skills](https://cursor.com/docs/context/skills) | `.agents/skills/`, `.cursor/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` | Only as a marketplace plugin |
| GitHub Copilot | [about skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [create skills](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills) | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` | `gh skill install OWNER/REPO SKILL` |
| `skills` CLI | [vercel-labs/skills](https://github.com/vercel-labs/skills), [skills.sh](https://skills.sh) | Installs into each agent's dir | Same | `npx skills add owner/repo` |

`.agents/skills/` is the closest thing to a shared project location: Codex, OpenCode,
Antigravity, Gemini CLI, Cursor, Copilot and the community grok-cli all read it. Claude Code reads
only `.claude/skills/`, and Grok Build reads `.grok/skills/` for project skills.

## Writing a skill that works everywhere

Write to the spec's limits and every tool above accepts it:

- **`name`**: 1-64 characters, lowercase `a-z`, `0-9` and single hyphens, no leading or trailing
  hyphen, and equal to the folder name.
- **`description`**: at most 1024 characters. Say what the skill does and when to use it; the
  description is what the agent matches a task against.
- **Spec-level optional fields**: `license`, `compatibility` (at most 500 characters),
  `metadata` (string map), `allowed-tools` (experimental).
- **Keep tool-specific fields optional.** Tools ignore fields they don't know, so a field like
  Claude Code's `argument-hint` is harmless elsewhere, but nothing should depend on it.
- **Describe behavior, not one tool's API.** Say "run it in the background with a deadline", then
  name a tool's specific mechanism as an example.

## Tool-specific extras

- **Claude Code** accepts the most frontmatter (`when_to_use`, `allowed-tools`, `context: fork`,
  `model`, `effort`, `paths`, `hooks`, `arguments` and more; description plus `when_to_use` share
  a 1536-character cap). Plugins can also ship hooks and user options, which is how this kit's
  hooks are delivered.
- **Codex CLI** reads an optional `agents/openai.yaml` next to `SKILL.md` for UI metadata,
  implicit-invocation policy and MCP dependencies. Codex supports
  [hooks](https://learn.chatgpt.com/docs/hooks) in its own format, and reads
  [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- **OpenCode** documents `license`, `compatibility` and `metadata`, and ignores unknown fields.
  Rules come from `AGENTS.md`, falling back to `CLAUDE.md` ([rules](https://opencode.ai/docs/rules/)).
- **Antigravity** requires only `description`. Rules come from `AGENTS.md` or `GEMINI.md`
  ([rules](https://antigravity.google/docs/rules)); hooks live in `.agents/hooks.json`
  ([hooks](https://antigravity.google/docs/hooks)).
- **Grok Build** adds `when-to-use`, `paths`, `allowed-tools`, `argument-hint`,
  `user-invocable` and `disable-model-invocation`.
- **Cursor** adds `paths`, `disable-model-invocation`, `icon` and `color`.
- **`skills` CLI**: `metadata.internal: true` hides a skill from listings. Its global install
  paths for Codex and Antigravity differ from those tools' own docs; if a skill doesn't show up
  after a global install, move it to the directory the tool's docs name.

## What this kit ships per tool

| Piece | Claude Code | Codex CLI | Others |
| --- | --- | --- | --- |
| 12 skills | Plugin | Plugin | `npx skills add`, or copy `plugins/agent-ship-kit/skills/*` into the tool's skills dir |
| House rules | `templates/HOUSE-RULES.md` | `AGENTS.md` | `AGENTS.md` |
| Hooks (kickoff card, context guard, LSP-first) | Plugin, toggled in plugin options | Not ported | Not ported |
