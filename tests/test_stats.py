"""Tests for cronparse.stats."""
from datetime import datetime

import pytest

from cronparse.history import CronHistory
from cronparse.stats import CronStats, compute_stats, history_stats

# Fixed reference so tests are deterministic
REF = datetime(2024, 6, 1, 12, 0)


class TestComputeStats:
    def test_returns_cron_stats_instance(self):
        result = compute_stats("* * * * *", reference=REF)
        assert isinstance(result, CronStats)

    def test_every_minute_runs_per_hour(self):
        stats = compute_stats("* * * * *", reference=REF)
        assert stats.runs_per_hour == 60

    def test_every_minute_runs_per_day(self):
        stats = compute_stats("* * * * *", reference=REF)
        assert stats.runs_per_day == 1440

    def test_hourly_runs_per_day(self):
        stats = compute_stats("0 * * * *", reference=REF)
        assert stats.runs_per_day == 24

    def test_daily_runs_per_week(self):
        stats = compute_stats("0 9 * * *", reference=REF)
        assert stats.runs_per_week == 7

    def test_next_5_runs_count(self):
        stats = compute_stats("* * * * *", reference=REF)
        assert len(stats.next_5_runs) == 5

    def test_next_5_runs_are_datetimes(self):
        stats = compute_stats("0 * * * *", reference=REF)
        for dt in stats.next_5_runs:
            assert isinstance(dt, datetime)

    def test_label_stored(self):
        stats = compute_stats("* * * * *", label="my job", reference=REF)
        assert stats.label == "my job"

    def test_expression_stored(self):
        expr = "30 6 * * 1"
        stats = compute_stats(expr, reference=REF)
        assert stats.expression == expr

    def test_str_contains_expression(self):
        stats = compute_stats("* * * * *", reference=REF)
        assert "* * * * *" in str(stats)

    def test_str_contains_next_runs_header(self):
        stats = compute_stats("* * * * *", reference=REF)
        assert "Next 5 runs" in str(stats)


class TestHistoryStats:
    def _make_history(self):
        h = CronHistory()
        h.add("* * * * *", label="every minute")
        h.add("0 9 * * *", label="daily")
        return h

    def test_returns_list(self):
        result = history_stats(self._make_history(), reference=REF)
        assert isinstance(result, list)

    def test_length_matches_history(self):
        h = self._make_history()
        result = history_stats(h, reference=REF)
        assert len(result) == len(h.entries)

    def test_each_item_is_cron_stats(self):
        for item in history_stats(self._make_history(), reference=REF):
            assert isinstance(item, CronStats)

    def test_labels_preserved(self):
        result = history_stats(self._make_history(), reference=REF)
        labels = [s.label for s in result]
        assert "every minute" in labels
        assert "daily" in labels
