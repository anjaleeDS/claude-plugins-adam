#!/usr/bin/env python3
"""Create or replace the "Goals for tomorrow" section in an Obsidian session note."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path


SECTION = "## Goals for tomorrow"
SECTION_META_RE = re.compile(r"^<!-- source: daily-wrapup; updated: .* -->$", re.M)


def normalize_goals(raw: str) -> str:
    lines: list[str] = []
    for line in raw.splitlines():
        item = line.strip()
        if not item:
            continue
        item = re.sub(r"^[-*]\s+", "", item)
        item = re.sub(r"^\d+[.)]\s+", "", item)
        item = re.sub(r"^\[[ xX]\]\s+", "", item)
        item = re.sub(r"^- \[[ xX]\]\s+", "", item)
        if item:
            lines.append(f"- {item}")
    if not lines:
        raise SystemExit("No goals provided.")
    return "\n".join(lines)


def render_template(template_path: Path, date: str) -> str:
    if not template_path.exists():
        return f"---\ndate: {date}\ntype: session\ntags: [session]\n---\n"
    text = template_path.read_text(encoding="utf-8")
    text = text.replace('<% tp.date.now("YYYY-MM-DD") %>', date)
    return text.rstrip() + "\n"


def replace_section(existing: str, section_body: str, updated_at: str) -> str:
    new_section = f"{SECTION}\n\n<!-- source: daily-wrapup; updated: {updated_at} -->\n\n{section_body}\n"
    pattern = re.compile(rf"^{re.escape(SECTION)}\n.*?(?=^## |\Z)", re.M | re.S)
    if pattern.search(existing):
        updated = pattern.sub(new_section, existing).rstrip() + "\n"
    else:
        updated = existing.rstrip() + "\n\n" + new_section
    return SECTION_META_RE.sub(f"<!-- source: daily-wrapup; updated: {updated_at} -->", updated)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def valid_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be YYYY-MM-DD") from exc
    return value


def main() -> None:
    default_vault = os.environ.get("VAULT", os.path.expanduser("~/obsidian-vault"))

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goals", required=True, help="Goal text, one per line or as bullets.")
    parser.add_argument("--date", required=True, type=valid_date, help="Target session date, YYYY-MM-DD.")
    parser.add_argument(
        "--vault",
        default=default_vault,
        help="Obsidian vault root. Defaults to $VAULT env var or ~/obsidian-vault.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the updated note without writing.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser()
    note = vault / "sessions" / f"{args.date}.md"
    template = vault / "templates" / "daily-session.md"
    updated_at = datetime.now().astimezone().isoformat(timespec="seconds")

    if note.exists():
        existing = note.read_text(encoding="utf-8")
    else:
        existing = render_template(template, args.date)

    updated = replace_section(existing, normalize_goals(args.goals), updated_at)
    if args.dry_run:
        print(updated, end="")
        return

    atomic_write(note, updated)
    print(str(note))


if __name__ == "__main__":
    main()
