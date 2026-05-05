"""Tests for the next_run preview module."""

import pytest
from datetime import datetime
from cronparse.next_run import next_run
from cronparse.exceptions import CronParseError


BASE = datetime(2024, 1, 15, 12, 0)  # Monday 2024-01-15 12:00


class TestNextRun:
    def test_returns_correct_count(self):
        results = next_run("* * * * *", after=BASE, count=5)
        assert len(results) == 5

    def test_every_minute_increments_by_one(self):
        results = next_run("* * * * *", after=BASE, count=3)
        assert results[0] == datetime(2024, 1, 15, 12, 1)
        assert results[1] == datetime(2024, 1, 15, 12, 2)
        assert results[2] == datetime(2024, 1, 15, 12, 3)

    def test_specific_minute_and_hour(self):
        results = next_run("30 14 * * *", after=BASE, count=2)
        assert results[0] == datetime(2024, 1, 15, 14, 30)
        assert results[1] == datetime(2024, 1, 16, 14, 30)

    def test_specific_day_of_month(self):
        results = next_run("0 9 20 * *", after=BASE, count=1)
        assert results[0] == datetime(2024, 1, 20, 9, 0)

    def test_specific_month(self):
        results = next_run("0 0 1 6 *", after=BASE, count=1)
        assert results[0] == datetime(2024, 6, 1, 0, 0)

    def test_step_expression(self):
        results = next_run("*/15 * * * *", after=BASE, count=4)
        assert results[0] == datetime(2024, 1, 15, 12, 15)
        assert results[1] == datetime(2024, 1, 15, 12, 30)
        assert results[2] == datetime(2024, 1, 15, 12, 45)
        assert results[3] == datetime(2024, 1, 15, 13, 0)

    def test_invalid_expression_raises(self):
        with pytest.raises(CronParseError):
            next_run("invalid", after=BASE)

    def test_count_less_than_one_raises(self):
        with pytest.raises(ValueError):
            next_run("* * * * *", after=BASE, count=0)

    def test_defaults_to_now(self):
        results = next_run("* * * * *", count=1)
        assert len(results) == 1
        assert results[0] > datetime.now().replace(second=0, microsecond=0)

    def test_weekday_filter(self):
        # 0 = Monday in our parser; BASE is a Monday
        results = next_run("0 9 * * 0", after=BASE, count=2)
        for dt in results:
            assert dt.weekday() == 0  # Monday
