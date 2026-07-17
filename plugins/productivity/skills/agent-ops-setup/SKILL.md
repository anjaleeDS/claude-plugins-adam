---
name: agent-ops-setup
description: Initialize private, local operational tracking for scheduled AI agents. Use when discovering or registering Codex, Claude, launchd, or other schedule definitions; creating an append-only run ledger; or choosing an Obsidian-compatible summary destination without copying schedule contents or secrets.
---

# Agent Ops Setup

Create a local agent inventory, append-only JSONL run ledger, and Markdown summary target. Keep collection manual unless the user explicitly asks for scheduling or hooks.

## Initialize tracking

1. Ask for the tracking root when the user has a preference. Otherwise use `$AGENT_OPS_HOME` or `~/.local/share/agent-ops`.
2. Accept schedule files or directories with repeated `--schedule`. Add `--discover` only when the user wants safe discovery of common local schedule locations.
3. Run:

```bash
python3 scripts/agent_ops_setup.py init \
  --root "$TRACKING_ROOT" \
  --summary "$OBSIDIAN_COMPATIBLE_PATH" \
  --schedule /path/to/schedule
```

The script records only local references and format labels. It never copies or prints schedule contents, commands, environment variables, prompts, or credentials. Discovery uses a fixed allowlist rather than recursively scanning the home directory.

4. Report the config, ledger, and summary paths plus the number of schedule definitions registered. Do not display source paths unless the user explicitly requests them.

## Append run records

Record measured facts after a run:

```bash
python3 scripts/record_run.py \
  --ledger "$TRACKING_ROOT/runs.jsonl" \
  --run-id weekly-review-2026-07-17 \
  --agent weekly-review \
  --platform codex \
  --status succeeded \
  --started-at 2026-07-17T20:00:00Z \
  --ended-at 2026-07-17T20:02:00Z \
  --input-tokens 1200 \
  --output-tokens 300 \
  --source sessions=available \
  --source calendar=unavailable
```

Omit unknown values. The script calculates duration only from supplied timestamps, labels token fields as measured, and lists absent fields under `unavailable_fields`. It locks the ledger and performs one append write per record.

## Guardrails

- Keep all artifacts local and permission-restricted.
- Never copy schedule contents into config, ledger, summaries, or chat.
- Never record prompts, responses, environment variables, tokens, API keys, or full session paths.
- Never infer token counts, status, duration, or source availability.
- Never install hooks, launch agents, cron entries, or background collectors unless the user explicitly requests them.
- Preserve the ledger as append-only; correct a record by appending a new record with a new run ID or explicit supersession metadata.
