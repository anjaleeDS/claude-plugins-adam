# productivity plugin

End-of-session and end-of-day workflow skills for Claude Code.

## Skills

### `/productivity:wrapup`

Checks for loose ends before clearing context — uncommitted changes, unpushed commits, open PRs, incomplete tasks, running background jobs. Tells you it's safe to `/clear` or lists what to resolve first.

### `/productivity:daily-wrapup`

End-of-day operating loop. Reviews yesterday's goals, summarizes what you accomplished today, previews tomorrow's calendar, optionally checks your on-call schedule, surfaces outstanding requests, and helps you commit goals for tomorrow. Writes goal commits to your Obsidian vault session note (works with the `memory` plugin).

### `/productivity:budgetclaw-setup`

Installs [budgetclaw](https://github.com/RoninForge/budgetclaw) in monitor-only mode on macOS with local Notification Center alerts. Sets a daily spend cap and fires a debounced popup when you breach it — no external services.

### `/productivity:create-agent`

Guided interview that turns a job description into a ready-to-use Claude Code skill. Answer a few questions about the agent's purpose, audience, tools, and vault access — the skill writes a `SKILL.md` in `.claude/skills/<name>/` and optionally registers the agent in your Obsidian vault under `agents/<name>.md`.

## Install

```
claude plugin marketplace add adzuci/claude-plugins
claude plugin install productivity@adzuci-plugins
```
