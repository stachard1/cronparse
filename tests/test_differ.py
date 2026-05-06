"""Tests for cronparse.differ module."""

import pytest
from cronparse.differ import diff, CronDiff, FieldDiff
from cronparse.exceptions import CronParseError


class TestDiff:
    def test_returns_cron_diff_instance(self):
        result = diff("* * * * *", "0 * * * *")
        assert isinstance(result, CronDiff)

    def test_no_changes_when_identical(self):
        result = diff("0 12 * * 1", "0 12 * * 1")
        assert not result.has_changes
        assert result.changes == []

    def test_detects_single_field_change(self):
        result = diff("* * * * *", "0 * * * *")
        assert result.has_changes
        assert len(result.changes) == 1
        assert result.changes[0].field == "minute"
        assert result.changes[0].old_value == "*"
        assert result.changes[0].new_value == "0"

    def test_detects_multiple_field_changes(self):
        result = diff("* * * * *", "0 12 1 6 *")
        assert len(result.changes) == 4
        fields = [c.field for c in result.changes]
        assert "minute" in fields
        assert "hour" in fields
        assert "day_of_month" in fields
        assert "month" in fields

    def test_field_diff_str(self):
        fd = FieldDiff(field="hour", old_value="*", new_value="12")
        assert str(fd) == "hour: '*' -> '12'"

    def test_cron_diff_summary_no_changes(self):
        result = diff("* * * * *", "* * * * *")
        assert "No differences" in result.summary()

    def test_cron_diff_summary_with_changes(self):
        result = diff("* * * * *", "0 12 * * *")
        summary = result.summary()
        assert "minute" in summary
        assert "hour" in summary

    def test_cron_diff_str_delegates_to_summary(self):
        result = diff("* * * * *", "5 * * * *")
        assert str(result) == result.summary()

    def test_stores_original_expressions(self):
        result = diff("*/5 * * * *", "0 0 * * *")
        assert result.old_expression == "*/5 * * * *"
        assert result.new_expression == "0 0 * * *"

    def test_invalid_expression_raises(self):
        with pytest.raises(Exception):
            diff("invalid", "* * * * *")

    def test_step_vs_wildcard_detected(self):
        result = diff("*/15 * * * *", "* * * * *")
        assert result.has_changes
        assert result.changes[0].field == "minute"
        assert result.changes[0].old_value == "*/15"
