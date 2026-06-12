"""
install_hook.py — Install the SessionEnd hook script and register it in
~/.claude/settings.json.

Usage:
    python install_hook.py --vault VAULTPATH [--home HOME] [--now EPOCH_INT]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from lib import merge_session_end_hook, render_template

_SKILL_DIR = Path(__file__).resolve().parent.parent
_TEMPLATE_PATH = _SKILL_DIR / "templates" / "session-end.sh.tmpl"
_HOOK_CMD = "~/.claude/hooks/session-end.sh"


def _backup_path(base: Path, now: int) -> Path:
    return base.parent / f"{base.name}.bak-{now}"


def _load_settings(path: Path) -> tuple[dict, bool]:
    """Return (settings_dict, was_malformed).  Missing → ({}, False)."""
    if not path.exists():
        return {}, False
    try:
        return json.loads(path.read_text()), False
    except json.JSONDecodeError:
        return {}, True


def install(vault: str, home: Path, now: int) -> dict:
    hooks_dir = home / ".claude" / "hooks"
    hook_script = hooks_dir / "session-end.sh"
    settings_path = home / ".claude" / "settings.json"

    # Validate settings before mutating the filesystem. A malformed settings
    # file must stop the install without replacing the hook script.
    settings, was_malformed = _load_settings(settings_path)

    if was_malformed:
        bak = _backup_path(settings_path, now)
        backup_ok = True
        try:
            import shutil
            shutil.copy2(str(settings_path), str(bak))
        except OSError as exc:
            backup_ok = False
            bak = f"{bak} (backup FAILED: {exc})"
        return {
            "ok": False,
            "backup_ok": backup_ok,
            "error": f"settings.json is malformed JSON. Backed up to {bak}. "
                     "Please fix manually before re-running.",
            "backup": str(bak),
        }

    # --- Render hook script from template ---
    template_text = _TEMPLATE_PATH.read_text()
    try:
        rendered = render_template(template_text, {"VAULT": vault})
    except ValueError as e:
        return {"ok": False, "error": f"Template rendering failed: {e}"}

    # Write hook script
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_script.write_text(rendered)
    hook_script.chmod(0o755)

    # Backup settings before writing
    if settings_path.exists():
        bak = _backup_path(settings_path, now)
        import shutil
        shutil.copy2(str(settings_path), str(bak))
    else:
        bak = None

    # Merge hook
    new_settings = merge_session_end_hook(settings, _HOOK_CMD)

    # Write new settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(new_settings, indent=2) + "\n")

    return {
        "ok": True,
        "hook_script": str(hook_script),
        "settings": str(settings_path),
        "settings_backup": str(bak) if bak else None,
        "vault": vault,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Install SessionEnd hook for memory vault.")
    parser.add_argument("--vault", required=True, help="Path to the Obsidian vault.")
    parser.add_argument("--home", default=None, help="Override home directory.")
    parser.add_argument("--now", type=int, default=None,
                        help="Epoch timestamp for backups (default: current time).")
    args = parser.parse_args()

    home = Path(args.home).expanduser() if args.home else Path.home()
    now = args.now if args.now is not None else int(time.time())

    result = install(vault=args.vault, home=home, now=now)
    print(json.dumps(result, indent=2))
    if not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
