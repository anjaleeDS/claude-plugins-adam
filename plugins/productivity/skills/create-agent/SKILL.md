---
name: create-agent
description: Guided interview that turns a job description into a ready-to-use Claude Code skill. Asks a few questions about the agent's purpose, audience, tools, and vault access, then generates a SKILL.md in .claude/skills/<name>/ and optionally registers it in your Obsidian vault under agents/<name>.md.
disable-model-invocation: true
---

# Create Agent

Turn a short interview into a working agent skill in minutes. Given an existing
memory vault, you answer a few questions and get a ready-to-use `SKILL.md` plus an
optional vault entry that records what the agent is for.

Keep the interview fast and concrete. Prefer sensible defaults over long questions.
Never invent tools or capabilities the user did not confirm.

## Step 1: Interview

Ask these as a single compact set of questions. Offer a default for each so the user
can accept quickly. Do not proceed until name and job are answered.

1. **Name** — short, kebab-case (e.g. `release-notes`, `standup-digest`). This becomes
   the skill directory and the `name` in frontmatter.
2. **Job** — what does it do, and for whom? One or two sentences. Capture the audience
   (a role, a team, or the user themselves).
3. **Inputs** — what does it need to start? (a link, pasted text, an argument, a question)
4. **Tools / skills** — which tools, MCP servers, CLIs, or other skills does it rely on?
   Mark any that are optional. If unsure, default to none.
5. **Reads vault?** — should it read the Obsidian vault for context (yes/no)? If yes,
   note which paths matter. Default: no.
6. **Guardrails** — anything it must never do, or where it should stop and ask.
   Default guardrail: read-only unless the user explicitly asks for changes; never put
   secrets in output.

## Step 2: Resolve paths

- `AGENT_NAME` = the kebab-case name.
- Skill target: `.claude/skills/$AGENT_NAME/SKILL.md` (project-local `.claude/`; if the
  user wants it globally available, use `$HOME/.claude/skills/$AGENT_NAME/SKILL.md`).
- Vault target (optional): `VAULT="${VAULT:-$HOME/obsidian-vault}"`,
  file `$VAULT/agents/$AGENT_NAME.md`.

If a file already exists at either target, show the path and ask before overwriting.

## Step 3: Generate the skill

Write `SKILL.md` to the skill target with this exact shape:

- **Frontmatter**: `name` (the kebab-case name) and `description` (one sentence that
  names what it does and who for, phrased so the model knows when to use it).
- **Job brief**: 1-2 sentences restating the job and audience.
- **Inputs**: what it needs to start.
- **Workflow**: numbered steps derived from the job. Be specific; each step should be an
  observable action. Include a final step for how it reports back or where it saves output.
- **Guardrails**: an explicit bulleted list from the interview plus the read-only default.

Do not add tools or steps the user did not describe. If the user named tools, reference
them in the relevant workflow steps and mark optional ones as skippable when unavailable.

## Step 4: Register in the vault (optional)

If the user said yes to vault registration, and `$VAULT/agents/` exists, write
`$VAULT/agents/$AGENT_NAME.md` from the vault's `agents/_template.md`, filling in the
frontmatter (`name`, `audience`, `reads_vault`, `skill_path`, `status: active`) and the
Job Brief, Tools & Skills, Workflow, and Guardrails from the interview.

If `$VAULT/agents/` does not exist, say so and skip this step rather than creating the vault.

## Step 5: Report

Print:

- The skill path written and how to invoke it (`/<name>` for a project skill,
  `/productivity:create-agent` generated it).
- The vault entry path if one was written.
- A one-line reminder that the user can edit the generated `SKILL.md` directly and
  re-run `/productivity:create-agent` to regenerate.

## Guardrails

- Only write to the two target paths above; never touch other files.
- Confirm before overwriting an existing skill or vault entry.
- Keep generated skills honest — no tools, permissions, or claims the user did not confirm.
- Do not create or modify `settings.json`, hooks, or configuration files.
