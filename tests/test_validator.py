"""Tests for cronparse.validator module."""

import pytest
from cronparse.validator import validate, ValidationResult


class TestValidate:
    def test_valid_expression_returns_true(self):
        result = validate("*/5 * * * *")
        assert result.is_valid is True
        assert result.errors == []

    def test_invalid_field_count_too_few(self):
        result = validate("* * * *")
        assert result.is_valid is False
        assert any("5 fields" in e for e in result.errors)

    def test_invalid_field_count_too_many(self):
        result = validate("* * * * * *")
        assert result.is_valid is False
        assert any("5 fields" in e for e in result.errors)

    def test_out_of_range_minute(self):
        result = validate("60 * * * *")
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_out_of_range_hour(self):
        result = validate("0 25 * * *")
        assert result.is_valid is False

    def test_invalid_month_name(self):
        result = validate("0 0 * FOO *")
        assert result.is_valid is False

    def test_valid_named_month(self):
        result = validate("0 9 * JAN *")
        assert result.is_valid is True

    def test_valid_named_dow(self):
        result = validate("0 8 * * MON")
        assert result.is_valid is True

    def test_str_valid(self):
        result = validate("0 0 * * *")
        assert str(result) == "Valid cron expression"

    def test_str_invalid(self):
        result = validate("99 * * * *")
        assert "Invalid cron expression" in str(result)

    def test_warning_both_dom_and_dow_restricted(self):
        result = validate("0 12 15 * MON")
        assert result.is_valid is True
        assert any("day-of-month" in w and "day-of-week" in w for w in result.warnings)

    def test_warning_every_minute(self):
        result = validate("* * * * *")
        assert result.is_valid is True
        assert any("every minute" in w for w in result.warnings)

    def test_no_warning_specific_time(self):
        result = validate("30 14 * * *")
        assert result.is_valid is True
        assert result.warnings == []

    def test_validation_result_dataclass(self):
        result = ValidationResult(is_valid=True, errors=[], warnings=["test"])
        assert result.is_valid is True
        assert result.warnings == ["test"]


class TestValidateEdgeCases:
    """Tests for boundary values and edge cases in cron field validation."""

    def test_minute_boundary_zero(self):
        result = validate("0 * * * *")
        assert result.is_valid is True

    def test_minute_boundary_max(self):
        result = validate("59 * * * *")
        assert result.is_valid is True

    def test_hour_boundary_zero(self):
        result = validate("0 0 * * *")
        assert result.is_valid is True

    def test_hour_boundary_max(self):
        result = validate("0 23 * * *")
        assert result.is_valid is True

    def test_day_of_month_boundary_max(self):
        result = validate("0 0 31 * *")
        assert result.is_valid is True

    def test_day_of_month_out_of_range(self):
        result = validate("0 0 32 * *")
        assert result.is_valid is False

    def test_step_value_in_range(self):
        result = validate("*/15 * * * *")
        assert result.is_valid is True

    def test_empty_string(self):
        result = validate("")
        assert result.is_valid is False
        assert len(result.errors) > 0
