"""Tests for cronparse.watchlist."""
import pytest
from datetime import datetime

from cronparse.watchlist import Watchlist, WatchEntry
from cronparse.exceptions import CronParseError


class TestWatchlist:
    def _make(self) -> Watchlist:
        return Watchlist()

    def test_add_returns_watch_entry(self):
        wl = self._make()
        entry = wl.add("* * * * *", "every-minute")
        assert isinstance(entry, WatchEntry)

    def test_add_stores_entry(self):
        wl = self._make()
        wl.add("0 9 * * 1", "weekly-monday")
        assert wl.get("weekly-monday") is not None

    def test_add_strips_label_whitespace(self):
        wl = self._make()
        wl.add("0 0 * * *", "  midnight  ")
        assert wl.get("midnight") is not None

    def test_add_invalid_expression_raises(self):
        wl = self._make()
        with pytest.raises(CronParseError):
            wl.add("99 * * * *", "bad")

    def test_add_empty_label_raises(self):
        wl = self._make()
        with pytest.raises(ValueError):
            wl.add("* * * * *", "")

    def test_add_whitespace_label_raises(self):
        wl = self._make()
        with pytest.raises(ValueError):
            wl.add("* * * * *", "   ")

    def test_remove_existing_returns_true(self):
        wl = self._make()
        wl.add("* * * * *", "job")
        assert wl.remove("job") is True

    def test_remove_missing_returns_false(self):
        wl = self._make()
        assert wl.remove("nonexistent") is False

    def test_remove_decrements_length(self):
        wl = self._make()
        wl.add("* * * * *", "a")
        wl.add("0 0 * * *", "b")
        wl.remove("a")
        assert len(wl) == 1

    def test_update_changes_expression(self):
        wl = self._make()
        wl.add("* * * * *", "job")
        wl.update("job", "0 6 * * *")
        assert wl.get("job").expression == "0 6 * * *"

    def test_update_sets_last_changed(self):
        wl = self._make()
        wl.add("* * * * *", "job")
        before = datetime.utcnow()
        wl.update("job", "0 6 * * *")
        assert wl.get("job").last_changed >= before

    def test_update_missing_label_raises(self):
        wl = self._make()
        with pytest.raises(KeyError):
            wl.update("ghost", "* * * * *")

    def test_update_invalid_expression_raises(self):
        wl = self._make()
        wl.add("* * * * *", "job")
        with pytest.raises(CronParseError):
            wl.update("job", "99 * * * *")

    def test_all_returns_all_entries(self):
        wl = self._make()
        wl.add("* * * * *", "a")
        wl.add("0 0 * * *", "b")
        assert len(wl.all()) == 2

    def test_str_contains_expression(self):
        wl = self._make()
        entry = wl.add("0 12 * * *", "noon")
        assert "0 12 * * *" in str(entry)
