"""Tests for cronparse CLI including the diff subcommand."""

import json
import pytest
from unittest.mock import patch
from cronparse.cli import build_parser, main


class TestCLI:
    def _run(self, argv, capsys):
        """Helper to invoke main() with given argv."""
        with patch("sys.argv", ["cronparse"] + argv):
            try:
                main()
            except SystemExit as exc:
                return exc.code, capsys.readouterr()
        return 0, capsys.readouterr()

    def test_valid_expression_exits_zero(self, capsys):
        code, _ = self._run(["* * * * *"], capsys)
        assert code == 0

    def test_invalid_expression_exits_one(self, capsys):
        code, _ = self._run(["99 * * * *"], capsys)
        assert code == 1

    def test_json_flag_produces_valid_json(self, capsys):
        code, captured = self._run(["--json", "0 12 * * *"], capsys)
        data = json.loads(captured.out)
        assert "expression" in data
        assert "is_valid" in data

    def test_json_next_runs_count_default(self, capsys):
        code, captured = self._run(["--json", "* * * * *"], capsys)
        data = json.loads(captured.out)
        assert len(data["next_runs"]) == 5

    def test_json_next_runs_count_custom(self, capsys):
        code, captured = self._run(["--json", "--next", "3", "* * * * *"], capsys)
        data = json.loads(captured.out)
        assert len(data["next_runs"]) == 3

    def test_no_expression_exits_one(self, capsys):
        code, _ = self._run([], capsys)
        assert code == 1

    def test_diff_subcommand_exits_zero(self, capsys):
        code, captured = self._run(["diff", "* * * * *", "0 12 * * *"], capsys)
        assert code == 0
        assert "minute" in captured.out

    def test_diff_subcommand_no_changes(self, capsys):
        code, captured = self._run(["diff", "0 12 * * *", "0 12 * * *"], capsys)
        assert code == 0
        assert "No differences" in captured.out

    def test_diff_json_output(self, capsys):
        code, captured = self._run(
            ["diff", "--json", "* * * * *", "0 12 * * *"], capsys
        )
        data = json.loads(captured.out)
        assert "changes" in data
        assert data["has_changes"] is True

    def test_diff_invalid_expression_exits_one(self, capsys):
        code, _ = self._run(["diff", "invalid", "* * * * *"], capsys)
        assert code == 1
