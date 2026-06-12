"""
Install an Antigravity SessionEnd hook that imports brain artifacts into the vault.
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import time
from pathlib import Path


_SKILL_DIR = Path(__file__).resolve().parent.parent
_IMPORTER = _SKILL_DIR / "scripts" / "antigravity_session_importer.py"


def _backup_path(base: Path, now: int) -> Path:
    return base.parent / f"{base.name}.bak-{now}"


def _load_hooks(path: Path) -> tuple[dict, bool]:
    if not path.exists():
        return {}, False
    try:
        return json.loads(path.read_text()), False
    except json.JSONDecodeError:
        return {}, True


def _command(vault: str) -> str:
    return f"python3 {shlex.quote(str(_IMPORTER))} --vault {shlex.quote(vault)}"


def _command_present(hooks: dict, command: str) -> bool:
    for entry in hooks.get("SessionEnd", []):
        for hook in entry.get("hooks", []):
            if hook.get("command") == command:
                return True
    return False


def merge_session_end_command(hooks: dict, command: str) -> dict:
    result = json.loads(json.dumps(hooks))
    if _command_present(result, command):
        return result
    session_end = result.setdefault("SessionEnd", [])
    session_end.append({"hooks": [{"type": "command", "command": command}]})
    return result


def install(vault: str, home: Path, now: int) -> dict:
    hooks_path = home / ".gemini" / "config" / "hooks.json"
    hooks, malformed = _load_hooks(hooks_path)
    if malformed:
        bak = _backup_path(hooks_path, now)
        shutil.copy2(str(hooks_path), str(bak))
        return {
            "ok": False,
            "error": f"hooks.json is malformed JSON. Backed up to {bak}.",
            "backup": str(bak),
        }

    command = _command(vault)
    new_hooks = merge_session_end_command(hooks, command)
    changed = new_hooks != hooks
    bak = None
    if changed and hooks_path.exists():
        bak_path = _backup_path(hooks_path, now)
        shutil.copy2(str(hooks_path), str(bak_path))
        bak = str(bak_path)
    if changed:
        hooks_path.parent.mkdir(parents=True, exist_ok=True)
        hooks_path.write_text(json.dumps(new_hooks, indent=2) + "\n")

    return {
        "ok": True,
        "hooks": str(hooks_path),
        "backup": bak,
        "command": command,
        "changed": changed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Antigravity SessionEnd importer hook.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--home", default=None, help="Override home directory.")
    parser.add_argument("--now", type=int, default=None)
    args = parser.parse_args()
    home = Path(args.home).expanduser() if args.home else Path.home()
    now = args.now if args.now is not None else int(time.time())
    print(json.dumps(install(args.vault, home, now), indent=2))


if __name__ == "__main__":
    main()
