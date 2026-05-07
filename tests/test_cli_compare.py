"""Tests for cronparse.cli_compare."""

from __future__ import annotations

import json
import types

import pytest

from cronparse.cli_compare import _run_compare, build_compare_parser


class _Args:
    def __init__(self, left: str, right: str, json: bool = False):
        self.left = left
        self.right = right
        self.json = json


class TestCliCompare:
    def test_identical_exits_zero(self, capsys):
        args = _Args("* * * * *", "* * * * *")
        code = _run_compare(args)
        assert code == 0

    def test_different_exits_two(self, capsys):
        args = _Args("0 9 * * *", "0 10 * * *")
        code = _run_compare(args)
        assert code == 2

    def test_invalid_left_exits_one(self, capsys):
        args = _Args("bad expr", "* * * * *")
        code = _run_compare(args)
        assert code == 1

    def test_invalid_right_exits_one(self, capsys):
        args = _Args("* * * * *", "99 * * * *")
        code = _run_compare(args)
        assert code == 1

    def test_json_flag_produces_valid_json(self, capsys):
        args = _Args("0 9 * * *", "0 10 * * *", json=True)
        _run_compare(args)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "identical" in data
        assert "fields" in data
        assert len(data["fields"]) == 5

    def test_json_identical_flag(self, capsys):
        args = _Args("0 9 * * 1", "0 9 * * 1", json=True)
        _run_compare(args)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["identical"] is True

    def test_text_output_contains_expressions(self, capsys):
        args = _Args("0 9 * * *", "0 10 * * *")
        _run_compare(args)
        captured = capsys.readouterr()
        assert "0 9 * * *" in captured.out
        assert "0 10 * * *" in captured.out

    def test_build_compare_parser_returns_parser(self):
        parser = build_compare_parser()
        assert parser is not None
