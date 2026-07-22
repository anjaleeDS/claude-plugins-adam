#!/usr/bin/env python3
"""Create a privacy-safe Markdown report from agent ledgers and JSONL artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOKEN_KEYS = {
    "input_tokens": "input",
    "output_tokens": "output",
    "cached_input_tokens": "cache_read",
    "cache_read_input_tokens": "cache_read",
    "cache_creation_input_tokens": "cache_creation",
    "total_tokens": "total",
}
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "partial"}


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    invalid = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                invalid += 1
                continue
            if isinstance(value, dict):
                records.append(value)
            else:
                invalid += 1
    return records, invalid


def metric_map(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for raw, normalized in TOKEN_KEYS.items():
        metric = value.get(raw)
        if isinstance(metric, int) and not isinstance(metric, bool) and metric >= 0:
            result[normalized] = metric
    return result


def find_codex_snapshots(value: Any) -> list[dict[str, int]]:
    found: list[dict[str, int]] = []
    if isinstance(value, dict):
        metrics = metric_map(value)
        if metrics:
            found.append(metrics)
        for child in value.values():
            found.extend(find_codex_snapshots(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_codex_snapshots(child))
    return found


def artifact_id(path: Path) -> str:
    digest = hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:12]
    return f"artifact-{digest}"


def explicit_status(records: list[dict[str, Any]]) -> str | None:
    for record in reversed(records):
        candidates = [record.get("status")]
        payload = record.get("payload")
        if isinstance(payload, dict):
            candidates.append(payload.get("status"))
        for value in candidates:
            if value in TERMINAL_STATUSES:
                return value
    return None


def normalize_artifact(path: Path) -> dict[str, Any]:
    records, invalid = read_jsonl(path)
    types = {record.get("type") for record in records}
    claude = bool(types & {"assistant", "user"}) and any(isinstance(r.get("message"), dict) for r in records)
    codex = bool(types & {"session_meta", "turn_context", "event_msg", "response_item"})
    style = "claude" if claude else "codex" if codex else "unknown"

    times: list[datetime] = []
    for record in records:
        for key in ("timestamp", "created_at", "started_at", "ended_at"):
            parsed = parse_time(record.get(key))
            if parsed:
                times.append(parsed)

    tokens: dict[str, int] = {}
    if style == "claude":
        totals: Counter[str] = Counter()
        for record in records:
            if record.get("type") != "assistant":
                continue
            message = record.get("message")
            usage = message.get("usage") if isinstance(message, dict) else None
            totals.update(metric_map(usage))
        tokens = dict(totals)
    elif style == "codex":
        snapshots: list[dict[str, int]] = []
        for record in records:
            if record.get("type") == "event_msg":
                snapshots.extend(find_codex_snapshots(record.get("payload")))
        if snapshots:
            tokens = snapshots[-1]

    unavailable: list[str] = []
    status = explicit_status(records)
    if status is None:
        unavailable.append("status")
    duration_ms = None
    if len(times) >= 2:
        duration_ms = int((max(times) - min(times)).total_seconds() * 1000)
    else:
        unavailable.append("duration")
    if not tokens:
        unavailable.append("tokens")
    if style == "unknown":
        unavailable.append("artifact_format")
    if invalid:
        unavailable.append("complete_parse")

    return {
        "run_id": artifact_id(path),
        "agent": "session-artifact",
        "platform": style,
        "status": status,
        "started_at": min(times).isoformat() if times else None,
        "ended_at": max(times).isoformat() if times else None,
        "duration_ms": duration_ms,
        "tokens": {"measurement": "measured", **tokens} if tokens else None,
        "sources": {"artifact": "partial" if invalid or style == "unknown" else "available"},
        "unavailable_fields": unavailable,
        "parse": {"valid_lines": len(records), "invalid_lines": invalid},
    }


def normalize_ledger(path: Path) -> tuple[list[dict[str, Any]], int]:
    records, invalid = read_jsonl(path)
    normalized: list[dict[str, Any]] = []
    for record in records:
        if record.get("record_type") != "agent_run":
            invalid += 1
            continue
        normalized.append(record)
    return normalized, invalid


def in_range(run: dict[str, Any], since: datetime | None, until: datetime | None) -> bool:
    observed = parse_time(run.get("started_at")) or parse_time(run.get("ended_at"))
    if observed is None:
        return since is None and until is None
    return not ((since and observed < since) or (until and observed > until))


def token_text(tokens: Any) -> str:
    if not isinstance(tokens, dict) or tokens.get("measurement") != "measured":
        return "unavailable"
    order = (("input", "in"), ("output", "out"), ("cache_read", "cache-read"), ("cache_creation", "cache-create"), ("total", "total"))
    shown = [f"{label}={tokens[key]}" for key, label in order if isinstance(tokens.get(key), int)]
    return ", ".join(shown) if shown else "unavailable"


def duration_text(value: Any) -> str:
    if not isinstance(value, int) or value < 0:
        return "unavailable"
    seconds = value / 1000
    return f"{seconds:.3f}s" if seconds < 60 else f"{seconds / 60:.2f}m"


def safe_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render(runs: list[dict[str, Any]], ledger_invalid: int) -> str:
    status_counts = Counter(run.get("status") or "unavailable" for run in runs)
    source_counts: Counter[str] = Counter()
    for run in runs:
        sources = run.get("sources")
        if isinstance(sources, dict):
            source_counts.update(str(value) for value in sources.values())

    lines = [
        "# Agent operations report",
        "",
        "Generated on demand from local metadata. Session prompts, responses, working directories, and source paths are excluded.",
        "",
        "## Coverage",
        "",
        f"- Runs: {len(runs)}",
        f"- Statuses: {', '.join(f'{k}={v}' for k, v in sorted(status_counts.items())) or 'none'}",
        f"- Source coverage: {', '.join(f'{k}={v}' for k, v in sorted(source_counts.items())) or 'unavailable'}",
        f"- Invalid ledger lines: {ledger_invalid}",
        "",
        "## Runs",
        "",
        "| Run | Agent | Platform | Status | Duration | Measured tokens | Sources | Unavailable fields |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for run in sorted(runs, key=lambda item: (item.get("started_at") or "", item.get("run_id") or "")):
        sources = run.get("sources") if isinstance(run.get("sources"), dict) else {}
        source_text = ", ".join(f"{k}={v}" for k, v in sorted(sources.items())) or "unavailable"
        unavailable = run.get("unavailable_fields") if isinstance(run.get("unavailable_fields"), list) else []
        unavailable_text = ", ".join(map(str, unavailable)) or "none"
        row = [
            run.get("run_id") or "unavailable",
            run.get("agent") or "unavailable",
            run.get("platform") or "unavailable",
            run.get("status") or "unavailable",
            duration_text(run.get("duration_ms")),
            token_text(run.get("tokens")),
            source_text,
            unavailable_text,
        ]
        lines.append("| " + " | ".join(safe_cell(value) for value in row) + " |")
    lines.append("")
    return "\n".join(lines)


def iso_arg(value: str) -> datetime:
    parsed = parse_time(value)
    if parsed is None:
        raise argparse.ArgumentTypeError("use a timezone-aware ISO timestamp")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", action="append", default=[])
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--since", type=iso_arg)
    parser.add_argument("--until", type=iso_arg)
    parser.add_argument("--output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.ledger and not args.artifact:
        raise SystemExit("provide at least one --ledger or --artifact")
    runs: list[dict[str, Any]] = []
    invalid = 0
    for raw in args.ledger:
        records, bad = normalize_ledger(Path(raw).expanduser())
        runs.extend(records)
        invalid += bad
    runs.extend(normalize_artifact(Path(raw).expanduser()) for raw in args.artifact)
    runs = [run for run in runs if in_range(run, args.since, args.until)]
    report = render(runs, invalid)
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
