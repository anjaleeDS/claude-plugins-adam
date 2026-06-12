"""
test_merge_claude_md.py — Insert / replace / idempotent tests for upsert_claude_md
against realistic CLAUDE.md string fixtures.
"""
from __future__ import annotations

from .conftest import load_script_module

lib = load_script_module("lib")

BEGIN = "<!-- BEGIN memory-setup (memory) -->"
END = "<!-- END memory-setup (memory) -->"

BLOCK_V1 = f"""{BEGIN}

## Memory: Session Capture + Vault

Vault location: `/home/user/my-vault`

<!-- END memory-setup (memory) -->"""

BLOCK_V2 = f"""{BEGIN}

## Memory: Session Capture + Vault (updated)

Vault location: `/home/user/new-vault`

<!-- END memory-setup (memory) -->"""

SAMPLE_CLAUDE_MD = """\
# My CLAUDE.md

## Mission

Be an excellent working partner.

## Non-Negotiables

Personal records are user-approved only.
"""


class TestUpsertClaudeMdInsert:
    """Block is inserted when markers are absent."""

    def test_block_appended(self) -> None:
        result = lib.upsert_claude_md(SAMPLE_CLAUDE_MD, BLOCK_V1, BEGIN, END)
        assert BLOCK_V1 in result

    def test_original_content_preserved(self) -> None:
        result = lib.upsert_claude_md(SAMPLE_CLAUDE_MD, BLOCK_V1, BEGIN, END)
        assert "## Mission" in result
        assert "Personal records are user-approved only." in result

    def test_blank_line_separator(self) -> None:
        """There should be a blank line before the block."""
        result = lib.upsert_claude_md(SAMPLE_CLAUDE_MD, BLOCK_V1, BEGIN, END)
        # The block must not be glued directly to the last line without separation
        idx_block = result.find(BEGIN)
        prefix = result[:idx_block]
        assert prefix.endswith("\n") or prefix.endswith("\n\n")

    def test_insert_into_empty_string(self) -> None:
        result = lib.upsert_claude_md("", BLOCK_V1, BEGIN, END)
        assert BLOCK_V1 in result

    def test_begin_marker_present_in_result(self) -> None:
        result = lib.upsert_claude_md(SAMPLE_CLAUDE_MD, BLOCK_V1, BEGIN, END)
        assert BEGIN in result

    def test_end_marker_present_in_result(self) -> None:
        result = lib.upsert_claude_md(SAMPLE_CLAUDE_MD, BLOCK_V1, BEGIN, END)
        assert END in result


class TestUpsertClaudeMdReplace:
    """Block is replaced in-place when markers are already present."""

    def _content_with_block(self, block: str) -> str:
        return SAMPLE_CLAUDE_MD + "\n\n" + block + "\n"

    def test_old_content_removed(self) -> None:
        existing = self._content_with_block(BLOCK_V1)
        result = lib.upsert_claude_md(existing, BLOCK_V2, BEGIN, END)
        assert "Vault location: `/home/user/my-vault`" not in result

    def test_new_content_present(self) -> None:
        existing = self._content_with_block(BLOCK_V1)
        result = lib.upsert_claude_md(existing, BLOCK_V2, BEGIN, END)
        assert "new-vault" in result

    def test_surrounding_content_preserved(self) -> None:
        existing = self._content_with_block(BLOCK_V1)
        result = lib.upsert_claude_md(existing, BLOCK_V2, BEGIN, END)
        assert "## Mission" in result
        assert "Personal records are user-approved only." in result

    def test_only_one_begin_marker(self) -> None:
        existing = self._content_with_block(BLOCK_V1)
        result = lib.upsert_claude_md(existing, BLOCK_V2, BEGIN, END)
        assert result.count(BEGIN) == 1

    def test_only_one_end_marker(self) -> None:
        existing = self._content_with_block(BLOCK_V1)
        result = lib.upsert_claude_md(existing, BLOCK_V2, BEGIN, END)
        assert result.count(END) == 1


class TestUpsertClaudeMdIdempotent:
    """Calling upsert_claude_md twice with the same block is a no-op."""

    def test_idempotent_on_insert(self) -> None:
        first = lib.upsert_claude_md(SAMPLE_CLAUDE_MD, BLOCK_V1, BEGIN, END)
        second = lib.upsert_claude_md(first, BLOCK_V1, BEGIN, END)
        assert first == second

    def test_idempotent_on_replace(self) -> None:
        # First replace V1 with V2
        existing = SAMPLE_CLAUDE_MD + "\n\n" + BLOCK_V1 + "\n"
        first = lib.upsert_claude_md(existing, BLOCK_V2, BEGIN, END)
        second = lib.upsert_claude_md(first, BLOCK_V2, BEGIN, END)
        assert first == second

    def test_idempotent_multiple_rounds(self) -> None:
        content = SAMPLE_CLAUDE_MD
        for _ in range(5):
            content = lib.upsert_claude_md(content, BLOCK_V1, BEGIN, END)
        assert content.count(BEGIN) == 1
