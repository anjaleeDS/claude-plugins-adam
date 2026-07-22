from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).parents[1]
SCRIPT = SKILL / "scripts" / "agent_ops_report.py"
spec = importlib.util.spec_from_file_location("agent_ops_report", SCRIPT)
reporter = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(reporter)


def write_jsonl(path: Path, values: list[object], invalid: bool = False) -> None:
    lines = [json.dumps(value) for value in values]
    if invalid:
        lines.append("{broken")
    path.write_text("\n".join(lines) + "\n")


class ReportTests(unittest.TestCase):
    def test_claude_usage_is_summed_and_content_is_not_emitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claude.jsonl"
            write_jsonl(path, [
                {"type": "user", "timestamp": "2026-07-17T10:00:00Z", "message": {"content": "PRIVATE PROMPT"}},
                {"type": "assistant", "timestamp": "2026-07-17T10:00:02Z", "message": {"content": "PRIVATE ANSWER", "usage": {"input_tokens": 10, "output_tokens": 4}}},
                {"type": "assistant", "timestamp": "2026-07-17T10:00:05Z", "message": {"usage": {"input_tokens": 3, "output_tokens": 2}}},
            ])
            run = reporter.normalize_artifact(path)
            rendered = reporter.render([run], 0)
            self.assertEqual(run["tokens"]["input"], 13)
            self.assertEqual(run["tokens"]["output"], 6)
            self.assertEqual(run["duration_ms"], 5000)
            self.assertNotIn("PRIVATE", rendered)
            self.assertNotIn(str(path), rendered)
            self.assertIn("status", run["unavailable_fields"])

    def test_codex_uses_latest_cumulative_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "codex.jsonl"
            write_jsonl(path, [
                {"type": "session_meta", "timestamp": "2026-07-17T10:00:00Z", "payload": {"id": "secret-session"}},
                {"type": "event_msg", "timestamp": "2026-07-17T10:00:01Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 10, "output_tokens": 3}}}},
                {"type": "event_msg", "timestamp": "2026-07-17T10:00:04Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 15, "output_tokens": 5}}}},
            ])
            run = reporter.normalize_artifact(path)
            self.assertEqual(run["tokens"]["input"], 15)
            self.assertEqual(run["tokens"]["output"], 5)
            self.assertEqual(run["platform"], "codex")

    def test_unknown_or_malformed_artifact_never_estimates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unknown.jsonl"
            write_jsonl(path, [{"note": "tokens 999 and success"}], invalid=True)
            run = reporter.normalize_artifact(path)
            self.assertIsNone(run["tokens"])
            self.assertIsNone(run["status"])
            self.assertIn("tokens", run["unavailable_fields"])
            self.assertIn("artifact_format", run["unavailable_fields"])
            self.assertIn("complete_parse", run["unavailable_fields"])

    def test_ledger_reports_explicit_unavailable_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runs.jsonl"
            write_jsonl(path, [{
                "record_type": "agent_run", "run_id": "r1", "agent": "reviewer",
                "platform": "claude", "status": "partial", "duration_ms": None,
                "tokens": None, "sources": {},
                "unavailable_fields": ["duration", "tokens", "source_coverage"],
            }])
            runs, invalid = reporter.normalize_ledger(path)
            rendered = reporter.render(runs, invalid)
            self.assertIn("duration, tokens, source_coverage", rendered)
            self.assertIn("unavailable", rendered)


if __name__ == "__main__":
    unittest.main()
