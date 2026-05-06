"""Tests for cronparse.overlap."""

from datetime import datetime

import pytest

from cronparse.overlap import OverlapResult, find_overlaps


START = datetime(2024, 1, 1, 0, 0)


class TestFindOverlaps:
    def test_returns_overlap_result(self):
        result = find_overlaps("* * * * *", "* * * * *", start=START, periods=5)
        assert isinstance(result, OverlapResult)

    def test_identical_expressions_all_overlap(self):
        result = find_overlaps("* * * * *", "* * * * *", start=START, periods=10)
        assert result.count == 10
        assert result.has_overlaps

    def test_no_overlap_different_hours(self):
        # runs at hour 3 vs hour 4 — no shared minutes within 60 periods
        result = find_overlaps("0 3 * * *", "0 4 * * *", start=START, periods=60)
        assert not result.has_overlaps
        assert result.count == 0

    def test_overlapping_hourly_and_every_minute(self):
        # every hour on the hour overlaps with every minute
        result = find_overlaps("0 * * * *", "* * * * *", start=START, periods=120)
        assert result.has_overlaps

    def test_overlapping_times_are_sorted(self):
        result = find_overlaps("*/15 * * * *", "*/5 * * * *", start=START, periods=60)
        times = result.overlapping_times
        assert times == sorted(times)

    def test_expr_a_and_expr_b_stored(self):
        result = find_overlaps("0 9 * * *", "0 9 * * 1", start=START, periods=50)
        assert result.expr_a == "0 9 * * *"
        assert result.expr_b == "0 9 * * 1"

    def test_str_no_overlaps(self):
        result = find_overlaps("0 3 * * *", "0 4 * * *", start=START, periods=60)
        text = str(result)
        assert "No overlaps" in text
        assert "0 3 * * *" in text

    def test_str_with_overlaps(self):
        result = find_overlaps("* * * * *", "* * * * *", start=START, periods=3)
        text = str(result)
        assert "overlap" in text.lower()
        assert "3" in text

    def test_str_truncates_long_list(self):
        result = find_overlaps("* * * * *", "* * * * *", start=START, periods=20)
        text = str(result)
        assert "+" in text  # truncation indicator

    def test_default_start_does_not_raise(self):
        # Should not raise even without explicit start
        result = find_overlaps("0 * * * *", "0 * * * *", periods=5)
        assert isinstance(result, OverlapResult)
