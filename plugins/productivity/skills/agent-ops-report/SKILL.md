---
name: agent-ops-report
description: Generate privacy-safe operational reports from agent run ledgers and local Codex or Claude JSONL/session artifacts. Use when reviewing per-run status, measured duration and tokens, source coverage, unavailable fields, or scheduled-agent reliability without exposing prompts, responses, repository paths, or company-specific data.
disable-model-invocation: true
---

# Agent Ops Report

Build an on-demand Markdown report from the local agent-ops ledger and optional Codex or Claude session JSONL. Treat every absent metric as unavailable, never as zero.

## Generate a report

Run the deterministic reporter with one or more inputs:

```bash
python3 scripts/agent_ops_report.py \
  --ledger ~/.local/share/agent-ops/runs.jsonl \
  --artifact /path/to/codex-rollout.jsonl \
  --artifact /path/to/claude-session.jsonl \
  --output /path/in/an/obsidian-vault/agent-ops-summary.md
```

Use `--since` and `--until` with timezone-aware ISO timestamps to bound ledger records. Artifact-derived runs remain included only when their observed timestamps satisfy the same bounds.

The report includes:

- one row per ledger record or session artifact,
- status, duration, and token counts only when explicitly measured,
- source availability and parse coverage,
- an explicit list of unavailable fields,
- aggregate status and source-coverage counts.

## Interpret session artifacts

- Parse Claude assistant-message `usage` fields as incremental measured usage and sum only numeric counters.
- Parse Codex token-count snapshots defensively and use the latest explicit cumulative snapshot rather than summing snapshots.
- Derive duration only from at least two valid timezone-aware timestamps.
- Mark artifact status unavailable unless the artifact contains an explicit terminal status.
- Tolerate malformed JSONL lines, record their count, and continue.
- Do not read or emit prompt text, response text, tool arguments, environment variables, working directories, or absolute artifact paths.

## Guardrails

- Keep reporting local and on demand. Do not add watchers, hooks, cron entries, automations, or uploads unless explicitly requested.
- Never estimate tokens, cost, duration, success, or source availability.
- Never convert missing metrics to zero.
- Never include session content in the report, even for debugging.
- Prefer the append-only ledger as the source of explicit run status; treat raw session artifacts as partial observational evidence.
- State parse gaps and unsupported formats in `unavailable_fields` and source coverage.
