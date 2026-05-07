"""Tests for cronparse.cli_lint."""
import json
import subprocess
import sys

import pytest

from cronparse.cli_lint import _run_lint


class _Args:
    """Minimal stand-in for argparse.Namespace."""
    def __init__(self, expression: str, as_json: bool = False):
        self.expression = expression
        self.as_json = as_json


class TestCliLint:
    def test_clean_expression_exits_zero(self):
        assert _run_lint(_Args("0 9 * * 1")) == 0

    def test_expression_with_warnings_exits_one(self):
        assert _run_lint(_Args("* * * * *")) == 1

    def test_invalid_expression_exits_zero_no_crash(self):
        # lint() returns empty warnings for invalid; CLI exits 0
        assert _run_lint(_Args("99 * * * *")) == 0

    def test_json_flag_exits_zero_for_clean(self, capsys):
        rc = _run_lint(_Args("0 9 * * 1", as_json=True))
        assert rc == 0

    def test_json_flag_output_is_valid_json(self, capsys):
        _run_lint(_Args("* * * * *", as_json=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "expression" in data
        assert "clean" in data
        assert "warnings" in data

    def test_json_flag_clean_field_false_for_warnings(self, capsys):
        _run_lint(_Args("* * * * *", as_json=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["clean"] is False

    def test_json_flag_clean_field_true_for_ok(self, capsys):
        _run_lint(_Args("0 6 * * *", as_json=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["clean"] is True

    def test_json_warnings_have_required_keys(self, capsys):
        _run_lint(_Args("* * * * *", as_json=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        for w in data["warnings"]:
            assert "field" in w
            assert "code" in w
            assert "message" in w

    def test_text_output_contains_ok_for_clean(self, capsys):
        _run_lint(_Args("0 9 * * 1"))
        captured = capsys.readouterr()
        assert "OK" in captured.out

    def test_text_output_contains_warning_code(self, capsys):
        _run_lint(_Args("* * * * *"))
        captured = capsys.readouterr()
        assert "W002" in captured.out
