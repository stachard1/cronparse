"""Tests for cronparse.pin."""
import pytest

from cronparse.exceptions import CronParseError
from cronparse.pin import PinEntry, PinStore


class TestPinStore:
    def _make(self) -> PinStore:
        return PinStore()

    def test_pin_returns_pin_entry(self):
        store = self._make()
        result = store.pin("* * * * *")
        assert isinstance(result, PinEntry)

    def test_pin_stores_entry(self):
        store = self._make()
        store.pin("0 9 * * 1")
        assert len(store) == 1

    def test_pin_with_label(self):
        store = self._make()
        entry = store.pin("0 9 * * 1", label="Weekly Monday")
        assert entry.label == "Weekly Monday"

    def test_pin_strips_label_whitespace(self):
        store = self._make()
        entry = store.pin("* * * * *", label="  trimmed  ")
        assert entry.label == "trimmed"

    def test_pin_invalid_expression_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.pin("not a cron")

    def test_pin_duplicate_overwrites(self):
        store = self._make()
        store.pin("* * * * *", label="first")
        store.pin("* * * * *", label="second")
        assert len(store) == 1
        assert store.get("* * * * *").label == "second"

    def test_is_pinned_true(self):
        store = self._make()
        store.pin("5 4 * * *")
        assert store.is_pinned("5 4 * * *") is True

    def test_is_pinned_false(self):
        store = self._make()
        assert store.is_pinned("5 4 * * *") is False

    def test_unpin_removes_entry(self):
        store = self._make()
        store.pin("0 0 * * *")
        result = store.unpin("0 0 * * *")
        assert result is True
        assert len(store) == 0

    def test_unpin_missing_returns_false(self):
        store = self._make()
        assert store.unpin("0 0 * * *") is False

    def test_all_returns_list(self):
        store = self._make()
        store.pin("* * * * *")
        store.pin("0 12 * * *")
        entries = store.all()
        assert len(entries) == 2
        assert all(isinstance(e, PinEntry) for e in entries)

    def test_all_returns_copy(self):
        store = self._make()
        store.pin("* * * * *")
        entries = store.all()
        entries.clear()
        assert len(store) == 1

    def test_get_existing(self):
        store = self._make()
        store.pin("0 6 * * *", label="Morning")
        entry = store.get("0 6 * * *")
        assert entry is not None
        assert entry.label == "Morning"

    def test_get_missing_returns_none(self):
        store = self._make()
        assert store.get("0 6 * * *") is None

    def test_clear_removes_all(self):
        store = self._make()
        store.pin("* * * * *")
        store.pin("0 1 * * *")
        store.clear()
        assert len(store) == 0

    def test_str_with_label(self):
        entry = PinEntry(expression="0 9 * * 1", label="Monday")
        assert str(entry) == "Monday: 0 9 * * 1"

    def test_str_without_label(self):
        entry = PinEntry(expression="* * * * *")
        assert str(entry) == "* * * * *"
