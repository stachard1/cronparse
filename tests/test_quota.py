"""Tests for cronparse.quota."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from cronparse.exceptions import CronParseError
from cronparse.quota import QuotaCheckResult, QuotaEntry, QuotaStore


EXPR = "0 * * * *"  # hourly
EVERY_MIN = "* * * * *"


class TestQuotaStore:
    def _make(self) -> QuotaStore:
        return QuotaStore()

    def test_add_returns_quota_entry(self):
        store = self._make()
        entry = store.add(EXPR, max_runs=5, window_hours=1)
        assert isinstance(entry, QuotaEntry)

    def test_add_stores_entry(self):
        store = self._make()
        store.add(EXPR, max_runs=5, window_hours=1)
        assert len(store.all()) == 1

    def test_add_with_label(self):
        store = self._make()
        entry = store.add(EXPR, max_runs=5, window_hours=1, label="  my job  ")
        assert entry.label == "my job"

    def test_add_invalid_expression_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.add("not valid", max_runs=5, window_hours=1)

    def test_add_zero_max_runs_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add(EXPR, max_runs=0, window_hours=1)

    def test_add_zero_window_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add(EXPR, max_runs=5, window_hours=0)

    def test_remove_existing_returns_true(self):
        store = self._make()
        store.add(EXPR, max_runs=5, window_hours=1)
        assert store.remove(EXPR) is True
        assert store.all() == []

    def test_remove_missing_returns_false(self):
        store = self._make()
        assert store.remove(EXPR) is False

    def test_get_returns_entry(self):
        store = self._make()
        store.add(EXPR, max_runs=5, window_hours=1)
        entry = store.get(EXPR)
        assert entry is not None
        assert entry.expression == EXPR

    def test_get_missing_returns_none(self):
        store = self._make()
        assert store.get(EXPR) is None

    def test_check_no_runs(self):
        store = self._make()
        entry = store.add(EXPR, max_runs=5, window_hours=1)
        result = store.check(entry, [])
        assert isinstance(result, QuotaCheckResult)
        assert result.runs_in_window == 0
        assert result.exceeded is False

    def test_check_within_quota(self):
        store = self._make()
        entry = store.add(EXPR, max_runs=5, window_hours=1)
        now = datetime(2024, 1, 1, 12, 0)
        runs = [now - timedelta(minutes=i * 10) for i in range(3)]
        result = store.check(entry, runs)
        assert result.runs_in_window == 3
        assert result.exceeded is False

    def test_check_exceeds_quota(self):
        store = self._make()
        entry = store.add(EXPR, max_runs=2, window_hours=1)
        now = datetime(2024, 1, 1, 12, 0)
        runs = [now - timedelta(minutes=i * 5) for i in range(5)]
        result = store.check(entry, runs)
        assert result.runs_in_window == 5
        assert result.exceeded is True

    def test_check_excludes_old_runs(self):
        store = self._make()
        entry = store.add(EXPR, max_runs=5, window_hours=1)
        now = datetime(2024, 1, 1, 12, 0)
        runs = [
            now - timedelta(hours=2),  # outside window
            now - timedelta(minutes=30),  # inside
        ]
        result = store.check(entry, runs)
        assert result.runs_in_window == 1
        assert result.exceeded is False
