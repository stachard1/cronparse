"""Tests for cronparse.blackout."""

from datetime import datetime, time

import pytest

from cronparse.blackout import BlackoutStore, BlackoutWindow
from cronparse.exceptions import CronParseError


EXPR = "0 2 * * *"  # daily at 02:00
EVERY_MIN = "* * * * *"


def _make() -> BlackoutStore:
    return BlackoutStore()


class TestBlackoutStore:
    def test_add_returns_blackout_window(self):
        store = _make()
        result = store.add(EXPR, time(22, 0), time(6, 0))
        assert isinstance(result, BlackoutWindow)

    def test_add_stores_entry(self):
        store = _make()
        store.add(EXPR, time(22, 0), time(6, 0))
        assert len(store.all()) == 1

    def test_add_with_label(self):
        store = _make()
        win = store.add(EXPR, time(1, 0), time(5, 0), label="maintenance")
        assert win.label == "maintenance"

    def test_add_invalid_expression_raises(self):
        store = _make()
        with pytest.raises((CronParseError, Exception)):
            store.add("not a cron", time(1, 0), time(2, 0))

    def test_add_same_start_end_raises(self):
        store = _make()
        with pytest.raises(ValueError):
            store.add(EXPR, time(3, 0), time(3, 0))

    def test_windows_for_returns_matching_only(self):
        store = _make()
        store.add(EXPR, time(1, 0), time(3, 0))
        store.add(EVERY_MIN, time(4, 0), time(5, 0))
        assert len(store.windows_for(EXPR)) == 1
        assert len(store.windows_for(EVERY_MIN)) == 1

    def test_remove_deletes_all_windows_for_expression(self):
        store = _make()
        store.add(EXPR, time(1, 0), time(2, 0))
        store.add(EXPR, time(3, 0), time(4, 0))
        removed = store.remove(EXPR)
        assert removed == 2
        assert store.windows_for(EXPR) == []

    def test_remove_unknown_expression_returns_zero(self):
        store = _make()
        assert store.remove("0 5 * * *") == 0

    def test_is_blacked_out_within_window(self):
        store = _make()
        store.add(EXPR, time(22, 0), time(23, 59))
        dt = datetime(2024, 1, 15, 22, 30)
        assert store.is_blacked_out(EXPR, dt) is True

    def test_is_blacked_out_outside_window(self):
        store = _make()
        store.add(EXPR, time(22, 0), time(23, 59))
        dt = datetime(2024, 1, 15, 10, 0)
        assert store.is_blacked_out(EXPR, dt) is False

    def test_overnight_window_covers_midnight(self):
        store = _make()
        store.add(EXPR, time(23, 0), time(5, 0))
        assert store.is_blacked_out(EXPR, datetime(2024, 1, 15, 0, 30)) is True
        assert store.is_blacked_out(EXPR, datetime(2024, 1, 15, 23, 30)) is True
        assert store.is_blacked_out(EXPR, datetime(2024, 1, 15, 12, 0)) is False

    def test_str_representation(self):
        win = BlackoutWindow(EXPR, time(2, 0), time(4, 0), label="nightly")
        text = str(win)
        assert "02:00" in text
        assert "04:00" in text
        assert "nightly" in text

    def test_all_returns_copy(self):
        store = _make()
        store.add(EXPR, time(1, 0), time(2, 0))
        result = store.all()
        result.clear()
        assert len(store.all()) == 1
