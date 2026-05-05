"""Tests for the humanize module."""

import pytest
from cronparse.humanize import humanize
from cronparse.exceptions import CronParseError


class TestHumanize:
    def test_every_minute(self):
        result = humanize("* * * * *")
        assert "every minute" in result
        assert "every day" in result

    def test_specific_time_daily(self):
        result = humanize("30 9 * * *")
        assert "09:30" in result
        assert "every day" in result

    def test_specific_day_of_month(self):
        result = humanize("0 0 15 * *")
        assert "15" in result
        assert "every day" not in result

    def test_specific_month(self):
        result = humanize("0 12 1 6 *")
        assert "June" in result
        assert "12:00" in result

    def test_weekday(self):
        result = humanize("0 8 * * 1")
        assert "Tuesday" in result

    def test_multiple_weekdays(self):
        result = humanize("0 8 * * 1,2")
        assert "Tuesday" in result
        assert "Wednesday" in result

    def test_step_minutes(self):
        result = humanize("*/15 * * * *")
        assert "every day" in result

    def test_returns_string(self):
        assert isinstance(humanize("5 4 * * *"), str)

    def test_invalid_expression_raises(self):
        with pytest.raises(CronParseError):
            humanize("bad expression")

    def test_ends_with_period(self):
        result = humanize("* * * * *")
        assert result.endswith(".")
