from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


setup = load_module("agent_ops_setup", SKILL / "scripts" / "agent_ops_setup.py")


class SetupTests(unittest.TestCase):
    def test_initialize_references_but_does_not_copy_schedule_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            schedule = base / "automation.toml"
            schedule.write_text('schedule = "weekly"\nAPI_KEY = "do-not-copy"\n')
            result = setup.initialize(base / "ops", base / "vault" / "summary.md", [schedule])
            config_text = Path(result["config"]).read_text()
            self.assertNotIn("do-not-copy", config_text)
            self.assertEqual(json.loads(config_text)["schedule_definitions"][0]["kind"], "codex-automation")
            self.assertTrue(Path(result["ledger"]).exists())
            self.assertTrue(Path(result["summary"]).exists())

    def test_record_run_appends_and_marks_unknowns(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "runs.jsonl"
            cmd = [
                sys.executable,
                str(SKILL / "scripts" / "record_run.py"),
                "--ledger", str(ledger),
                "--run-id", "run-1",
                "--agent", "reviewer",
                "--platform", "claude",
                "--status", "succeeded",
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            second_cmd = cmd.copy()
            second_cmd[second_cmd.index("run-1")] = "run-2"
            subprocess.run(second_cmd, check=True, capture_output=True, text=True)
            records = [json.loads(line) for line in ledger.read_text().splitlines()]
            self.assertEqual([r["run_id"] for r in records], ["run-1", "run-2"])
            self.assertIn("tokens", records[0]["unavailable_fields"])
            self.assertIn("duration", records[0]["unavailable_fields"])
            self.assertIsNone(records[0]["tokens"])


if __name__ == "__main__":
    unittest.main()
