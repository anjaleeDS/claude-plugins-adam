# Setup Tracking

Use a local setup log as the default tracking surface. This keeps the skill portable and avoids requiring any specific project-management tool.

## Entry Format

Append this shape to `<vault>/setup-log.md`:

```markdown
## <name> setup - YYYY-MM-DD

- Client mode: Claude Code / Codex / Antigravity / shared
- Vault path: <vault>
- Git remote: <remote URL or local-only>
- Obsidian plugins: claudian, obsidian-git
- Issues hit:
  - none
```

If there were problems, replace `none` with concise bullets. Include only operational facts that would help the user debug or repeat the setup later.

## Optional External Trackers

If the user wants this mirrored into Notion, Linear, GitHub Issues, or another tracker, translate the same fields into that system after asking for approval. Do not block the memory setup on external tracker access.
