# claude-plugins

Public Claude Code and Codex plugins for personal operating-system workflows.

The first plugin in this repo is `memory`, a setup skill for creating a local, git-backed Obsidian vault that captures durable notes from AI working sessions.

## Why I Made This

I kept running into the same problem: AI sessions were useful in the moment, but the important parts were scattered across chats, local transcripts, repo state, and whatever I happened to remember later.

That is fine for one-off help. It is bad for real work. The value of an assistant compounds only when it can retain the shape of your projects, preferences, decisions, and recurring failure modes. Without a memory layer, every new session pays a tax: rediscover the project, restate the preferences, reconstruct the path, and hope nothing subtle was lost.

This skill is my attempt to make that memory layer boring and local:

- Use Obsidian because plain Markdown is inspectable and portable
- Use git because history should be auditable
- Use session-end capture because the best time to summarize is when the work is still warm
- Use explicit gates because tools that write to dotfiles should earn permission every step of the way
- Support more than one coding assistant because the memory should belong to the person, not the vendor

The goal is not to build a second brain for its own sake. The goal is to reduce re-orientation cost and make good context reusable.

## Plugins

| Plugin | Skill | Purpose |
| --- | --- | --- |
| `memory` | `/memory:memory-setup` | Set up an Obsidian-backed memory vault with Claude Code session capture and optional Codex/Antigravity importers. |

## Install

Claude Code marketplace metadata lives in `.claude-plugin/marketplace.json`.

Codex marketplace metadata lives in `.agents/plugins/marketplace.json`.

For Codex:

```bash
codex plugin marketplace add adzuci/claude-plugins
codex plugin marketplace upgrade adzuci-plugins
codex plugin add memory@adzuci-plugins
```

For Claude Code:

```bash
claude plugin marketplace add adzuci/claude-plugins
claude plugin install memory@adzuci-plugins
claude plugin enable memory
```

Then invoke the setup skill:

```text
/memory:memory-setup
```

## Repository Structure

```text
.claude-plugin/
  marketplace.json
.agents/
  plugins/
    marketplace.json
plugins/
  memory/
    .claude-plugin/plugin.json
    .codex-plugin/plugin.json
    README.md
    skills/memory-setup/
      SKILL.md
      scripts/
      templates/
      references/
      tests/
```

## Development

Run the memory skill tests:

```bash
python3 -m pytest plugins/memory/skills/memory-setup/tests -q
```

Validate the plugin metadata with the CLI available in your environment:

```bash
claude plugin validate .
```

## License

MIT
