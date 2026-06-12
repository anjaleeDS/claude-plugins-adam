# Memory

`memory` is a portable skill for setting up a local, git-backed Obsidian vault that captures useful AI working-session notes instead of letting them disappear into chat history.

Current support note: the setup flow has been tested on macOS. Linux and Windows compatibility reports and PRs are welcome.

It includes:

- `memory-setup` skill instructions for a gated, user-approved setup flow
- Python scripts for vault scaffolding, Obsidian plugin installation, Claude Code hook registration, and optional Codex/Antigravity imports
- Templates for the generated vault and the managed `CLAUDE.md` memory block
- Tests for the idempotent setup helpers

## Invoke

```text
/memory:memory-setup
```

## Install

From Codex:

```bash
codex plugin marketplace add adzuci/claude-plugins
codex plugin add memory@adzuci-plugins
```

From Claude Code:

```bash
claude plugin marketplace add adzuci/claude-plugins
claude plugin install memory@adzuci-plugins
```

## What It Installs

The default Claude Code path sets up:

- A local Obsidian vault under a user-selected parent directory
- `claudian` and `obsidian-git` as Obsidian community plugins
- A `SessionEnd` hook in `~/.claude/settings.json`
- A managed memory block in `~/.claude/CLAUDE.md`

Codex and Antigravity compatibility paths append summaries into the same vault without writing to `~/.claude` unless the user explicitly asks for shared Claude setup.

## Safety Model

The skill is deliberately gated. It explains the cost and trade-offs first, runs read-only preflight checks, asks for setup inputs, and requires approval before write steps.

Re-running is designed to be safe:

- Hook registration is idempotent
- `CLAUDE.md` updates replace one managed block
- Existing vault directories are not overwritten
- `claude-mem` cleanup is dry-run by default
- Session importers track already-ingested sessions
