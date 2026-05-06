"""Tests for cronparse.cli command-line interface."""

import json
import pytest

from cronparse.cli import main


class TestCLI:
    def test_valid_expression_exits_zero(self):
        code = main(["* * * * *", "--from", "2024-01-15T10:00:00"])
        assert code == 0

    def test_invalid_expression_exits_one(self):
        code = main(["99 * * * *", "--from", "2024-01-15T10:00:00"])
        assert code == 1

    def test_json_flag_produces_valid_json(self, capsys):
        main(["*/5 * * * *", "--from", "2024-01-15T10:00:00", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "expression" in data
        assert "next_runs" in data

    def test_json_next_runs_count_default(self, capsys):
        main(["* * * * *", "--from", "2024-01-15T10:00:00", "--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data["next_runs"]) == 5

    def test_json_next_runs_count_custom(self, capsys):
        main(["* * * * *", "--from", "2024-01-15T10:00:00", "--json", "--count", "3"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data["next_runs"]) == 3

    def test_plain_output_contains_expression(self, capsys):
        main(["0 9 * * *", "--from", "2024-01-15T08:00:00"])
        captured = capsys.readouterr()
        assert "0 9 * * *" in captured.out

    def test_invalid_from_datetime_exits_one(self, capsys):
        code = main(["* * * * *", "--from", "not-a-date"])
        assert code == 1

    def test_invalid_from_datetime_prints_error(self, capsys):
        main(["* * * * *", "--from", "not-a-date"])
        captured = capsys.readouterr()
        assert "Error" in captured.err
