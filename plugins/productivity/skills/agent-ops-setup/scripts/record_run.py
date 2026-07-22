#!/usr/bin/env python3
"""Append one measured agent run record to a local JSONL ledger."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_STATUS = ("succeeded", "failed", "cancelled", "partial", "unknown")
ALLOWED_SOURCE_STATUS = {"available", "partial", "unavailable", "not-requested"}


def parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def iso_time(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def parse_source(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("source must be NAME=STATUS")
    name, status = value.split("=", 1)
    if not name or status not in ALLOWED_SOURCE_STATUS:
        raise argparse.ArgumentTypeError("invalid source name or status")
    return name, status


def build_record(args: argparse.Namespace) -> dict[str, object]:
    duration_ms = None
    if args.started_at and args.ended_at:
        duration_ms = int((args.ended_at - args.started_at).total_seconds() * 1000)
        if duration_ms < 0:
            raise ValueError("ended-at must not precede started-at")

    token_values = {
        "input": args.input_tokens,
        "output": args.output_tokens,
        "cache_read": args.cache_read_tokens,
        "cache_creation": args.cache_creation_tokens,
        "total": args.total_tokens,
    }
    unavailable: list[str] = []
    if duration_ms is None:
        unavailable.append("duration")
    if not any(value is not None for value in token_values.values()):
        unavailable.append("tokens")
    if not args.source:
        unavailable.append("source_coverage")

    return {
        "schema_version": 1,
        "record_type": "agent_run",
        "run_id": args.run_id,
        "agent": args.agent,
        "platform": args.platform,
        "status": args.status,
        "started_at": iso_time(args.started_at) if args.started_at else None,
        "ended_at": iso_time(args.ended_at) if args.ended_at else None,
        "duration_ms": duration_ms,
        "tokens": {"measurement": "measured", **token_values} if any(v is not None for v in token_values.values()) else None,
        "sources": dict(args.source),
        "unavailable_fields": unavailable,
        "recorded_at": iso_time(datetime.now(timezone.utc)),
    }


def append_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n").encode()
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--status", choices=ALLOWED_STATUS, required=True)
    parser.add_argument("--started-at", type=parse_time)
    parser.add_argument("--ended-at", type=parse_time)
    parser.add_argument("--input-tokens", type=int)
    parser.add_argument("--output-tokens", type=int)
    parser.add_argument("--cache-read-tokens", type=int)
    parser.add_argument("--cache-creation-tokens", type=int)
    parser.add_argument("--total-tokens", type=int)
    parser.add_argument("--source", type=parse_source, action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    for value in (args.input_tokens, args.output_tokens, args.cache_read_tokens, args.cache_creation_tokens, args.total_tokens):
        if value is not None and value < 0:
            raise SystemExit("token counts must be non-negative")
    try:
        record = build_record(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    append_record(Path(args.ledger).expanduser(), record)
    print(json.dumps({"appended": True, "run_id": args.run_id}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
