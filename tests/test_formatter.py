"""Tests for cronparse.formatter.summarize and CronSummary."""

from datetime import datetime
import pytest

from cronparse.formatter import summarize, CronSummary


FIXED_DT = datetime(2024, 1, 15, 12, 0, 0)


class TestSummarize:
    def test_returns_cron_summary_instance(self):
        result = summarize("* * * * *", from_dt=FIXED_DT)
        assert isinstance(result, CronSummary)

    def test_valid_expression_is_valid(self):
        result = summarize("*/5 * * * *", from_dt=FIXED_DT)
        assert result.is_valid is True

    def test_invalid_expression_is_not_valid(self):
        result = summarize("99 * * * *", from_dt=FIXED_DT)
        assert result.is_valid is False

    def test_next_runs_count_respected(self):
        result = summarize("* * * * *", from_dt=FIXED_DT, count=3)
        assert len(result.next_runs) == 3

    def test_next_runs_are_datetimes(self):
        result = summarize("0 9 * * *", from_dt=FIXED_DT, count=2)
        for dt in result.next_runs:
            assert isinstance(dt, datetime)

    def test_description_not_empty_for_valid(self):
        result = summarize("0 0 * * *", from_dt=FIXED_DT)
        assert result.description != ""

    def test_description_empty_for_invalid(self):
        result = summarize("abc * * * *", from_dt=FIXED_DT)
        assert result.description == ""

    def test_expression_preserved(self):
        expr = "30 8 * * 1"
        result = summarize(expr, from_dt=FIXED_DT)
        assert result.expression == expr

    def test_to_dict_keys(self):
        result = summarize("* * * * *", from_dt=FIXED_DT, count=1)
        d = result.to_dict()
        assert set(d.keys()) == {"expression", "description", "is_valid", "validation_message", "next_runs"}

    def test_to_dict_next_runs_are_strings(self):
        result = summarize("* * * * *", from_dt=FIXED_DT, count=2)
        d = result.to_dict()
        for s in d["next_runs"]:
            assert isinstance(s, str)

    def test_str_output_contains_expression(self):
        expr = "0 12 * * *"
        result = summarize(expr, from_dt=FIXED_DT)
        assert expr in str(result)

    def test_str_output_invalid_shows_error(self):
        result = summarize("99 * * * *", from_dt=FIXED_DT)
        assert "Error" in str(result)
