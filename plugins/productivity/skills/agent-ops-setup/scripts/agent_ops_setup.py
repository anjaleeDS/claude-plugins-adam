#!/usr/bin/env python3
"""Initialize local agent operations tracking without reading schedule contents."""

from __future__ import annotations

import argparse
import json
import os
import stat
from pathlib import Path

SUPPORTED_SUFFIXES = {".json", ".jsonl", ".md", ".plist", ".toml", ".yaml", ".yml"}
DISCOVERY_PATTERNS = (
    ".codex/automations/*/automation.toml",
    ".claude/agents/*.md",
    "Library/LaunchAgents/*agent*.plist",
)


def schedule_kind(path: Path) -> str:
    if path.name == "automation.toml":
        return "codex-automation"
    if path.suffix == ".plist":
        return "launchd-plist"
    if path.suffix == ".md":
        return "agent-markdown"
    return path.suffix.lstrip(".") or "unknown"


def expand_explicit(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        candidate = Path(raw).expanduser()
        if candidate.is_file():
            found.append(candidate)
        elif candidate.is_dir():
            found.extend(p for p in candidate.rglob("*") if p.is_file() and p.suffix in SUPPORTED_SUFFIXES)
        else:
            raise ValueError(f"schedule path does not exist: {raw}")
    return found


def discover(home: Path) -> list[Path]:
    return [p for pattern in DISCOVERY_PATTERNS for p in home.glob(pattern) if p.is_file()]


def write_private(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def initialize(root: Path, summary: Path, schedules: list[Path]) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=True)
    root.chmod(stat.S_IRWXU)
    summary.parent.mkdir(parents=True, exist_ok=True)
    ledger = root / "runs.jsonl"
    ledger.touch(exist_ok=True)
    ledger.chmod(stat.S_IRUSR | stat.S_IWUSR)

    unique = sorted({p.resolve() for p in schedules}, key=lambda p: str(p))
    config = {
        "schema_version": 1,
        "ledger": str(ledger.resolve()),
        "summary": str(summary.resolve()),
        "schedule_definitions": [
            {"path": str(path), "kind": schedule_kind(path)} for path in unique
        ],
        "privacy": {
            "schedule_contents_copied": False,
            "background_collection_enabled": False,
        },
    }
    config_path = root / "config.json"
    write_private(config_path, json.dumps(config, indent=2, sort_keys=True) + "\n")

    if not summary.exists():
        write_private(
            summary,
            "# Agent operations summary\n\n"
            "Generated on demand from the local append-only run ledger.\n",
        )
    else:
        summary.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return {
        "config": str(config_path.resolve()),
        "ledger": str(ledger.resolve()),
        "summary": str(summary.resolve()),
        "schedule_count": len(unique),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="initialize local tracking")
    init.add_argument("--root", default=os.environ.get("AGENT_OPS_HOME", "~/.local/share/agent-ops"))
    init.add_argument("--summary", help="Obsidian-compatible Markdown output path")
    init.add_argument("--schedule", action="append", default=[], help="schedule file or directory; repeatable")
    init.add_argument("--discover", action="store_true", help="check fixed common schedule locations")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).expanduser()
    summary = Path(args.summary).expanduser() if args.summary else root / "obsidian" / "agent-ops-summary.md"
    try:
        schedules = expand_explicit(args.schedule)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.discover:
        schedules.extend(discover(Path.home()))
    result = initialize(root, summary, schedules)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
