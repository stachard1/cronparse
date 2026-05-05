"""Tests for the CronExpression parser and validator."""

import pytest

from cronparse import CronExpression, CronParseError
from cronparse.exceptions import CronFieldError


class TestCronExpressionParsing:
    def test_wildcard_all_fields(self):
        expr = CronExpression("* * * * *")
        assert expr.minute == set(range(0, 60))
        assert expr.hour == set(range(0, 24))
        assert expr.day_of_month == set(range(1, 32))
        assert expr.month == set(range(1, 13))
        assert 0 in expr.day_of_week and 7 in expr.day_of_week

    def test_specific_values(self):
        expr = CronExpression("30 6 15 3 1")
        assert expr.minute == {30}
        assert expr.hour == {6}
        assert expr.day_of_month == {15}
        assert expr.month == {3}
        assert expr.day_of_week == {1}

    def test_range_field(self):
        expr = CronExpression("0-30 * * * *")
        assert expr.minute == set(range(0, 31))

    def test_step_field(self):
        expr = CronExpression("*/15 * * * *")
        assert expr.minute == {0, 15, 30, 45}

    def test_step_with_start(self):
        expr = CronExpression("5/10 * * * *")
        assert expr.minute == {5, 15, 25, 35, 45, 55}

    def test_list_field(self):
        expr = CronExpression("0,15,30,45 * * * *")
        assert expr.minute == {0, 15, 30, 45}

    def test_month_aliases(self):
        expr = CronExpression("0 0 1 Jan *")
        assert expr.month == {1}

        expr2 = CronExpression("0 0 1 dec *")
        assert expr2.month == {12}

    def test_dow_aliases(self):
        expr = CronExpression("0 0 * * Mon")
        assert expr.day_of_week == {1}

        expr2 = CronExpression("0 0 * * sun")
        assert expr2.day_of_week == {0}

    def test_combined_list_and_range(self):
        expr = CronExpression("1,5-10,20 * * * *")
        assert {1, 5, 6, 7, 8, 9, 10, 20}.issubset(expr.minute)


class TestCronExpressionValidation:
    def test_wrong_number_of_fields_raises(self):
        with pytest.raises(CronParseError):
            CronExpression("* * * *")

    def test_too_many_fields_raises(self):
        with pytest.raises(CronParseError):
            CronExpression("* * * * * *")

    def test_minute_out_of_range_raises(self):
        with pytest.raises(CronFieldError):
            CronExpression("60 * * * *")

    def test_hour_out_of_range_raises(self):
        with pytest.raises(CronFieldError):
            CronExpression("* 24 * * *")

    def test_month_out_of_range_raises(self):
        with pytest.raises(CronFieldError):
            CronExpression("* * * 13 *")

    def test_invalid_step_zero_raises(self):
        with pytest.raises(CronFieldError):
            CronExpression("*/0 * * * *")

    def test_inverted_range_raises(self):
        with pytest.raises(CronFieldError):
            CronExpression("30-10 * * * *")

    def test_invalid_token_raises(self):
        with pytest.raises(CronFieldError):
            CronExpression("abc * * * *")

    def test_error_message_contains_expression(self):
        bad = "99 * * * *"
        with pytest.raises(CronParseError) as exc_info:
            CronExpression(bad)
        assert bad in str(exc_info.value)
