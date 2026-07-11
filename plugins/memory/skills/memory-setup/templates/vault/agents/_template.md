---
type: agent
name:
audience:
reads_vault: false
skill_path:
status: draft
---

# Agent: <name>

## Job Brief

One or two sentences: what this agent does and who it does it for.

## Audience / Owner

Who relies on this agent (a role, a team, or yourself) and who maintains it.

## Inputs

What the agent needs to start: files, links, pasted text, arguments, or a question.

## Tools & Skills

Tools, MCP servers, CLIs, or other skills this agent depends on. Note any that are optional.

## Reads Vault?

Yes / No. If yes, list the paths it should read first (start from `index.md`) and what it may write.

## Workflow

1. Step one — the first thing it always does.
2. Step two — the core work.
3. Step three — how it reports back or where it saves output.

## Guardrails

- What it must never do (e.g. no writes without confirmation, no secrets in output).
- Where its authority stops and it should ask the user.
- Read-only unless explicitly asked to change things.

## Linked Skill

Path to the generated skill, e.g. `.claude/skills/<name>/SKILL.md`.
