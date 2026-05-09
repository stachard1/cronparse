"""Tests for cronparse.priority."""
import pytest

from cronparse.priority import PriorityEntry, PriorityLevel, PriorityQueue
from cronparse.exceptions import CronParseError


class TestPriorityQueue:
    def _make(self) -> PriorityQueue:
        return PriorityQueue()

    def test_add_returns_priority_entry(self):
        q = self._make()
        result = q.add("* * * * *")
        assert isinstance(result, PriorityEntry)

    def test_add_stores_entry(self):
        q = self._make()
        q.add("0 * * * *")
        assert len(q) == 1

    def test_add_invalid_expression_raises(self):
        q = self._make()
        with pytest.raises(CronParseError):
            q.add("not a cron")

    def test_add_with_label(self):
        q = self._make()
        entry = q.add("* * * * *", label="  my job  ")
        assert entry.label == "my job"

    def test_add_with_level(self):
        q = self._make()
        entry = q.add("* * * * *", level=PriorityLevel.HIGH)
        assert entry.level == PriorityLevel.HIGH

    def test_get_returns_all_entries(self):
        q = self._make()
        q.add("* * * * *")
        q.add("0 * * * *")
        assert len(q.get()) == 2

    def test_get_sorted_by_level_descending(self):
        q = self._make()
        q.add("* * * * *", level=PriorityLevel.LOW)
        q.add("0 * * * *", level=PriorityLevel.CRITICAL)
        q.add("0 0 * * *", level=PriorityLevel.NORMAL)
        levels = [e.level for e in q.get()]
        assert levels == sorted(levels, reverse=True)

    def test_get_filter_by_level(self):
        q = self._make()
        q.add("* * * * *", level=PriorityLevel.HIGH)
        q.add("0 * * * *", level=PriorityLevel.LOW)
        result = q.get(level=PriorityLevel.HIGH)
        assert len(result) == 1
        assert result[0].level == PriorityLevel.HIGH

    def test_remove_existing_entry(self):
        q = self._make()
        q.add("* * * * *")
        removed = q.remove("* * * * *")
        assert removed is True
        assert len(q) == 0

    def test_remove_nonexistent_returns_false(self):
        q = self._make()
        assert q.remove("* * * * *") is False

    def test_highest_returns_max_level_entry(self):
        q = self._make()
        q.add("* * * * *", level=PriorityLevel.LOW)
        q.add("0 * * * *", level=PriorityLevel.CRITICAL)
        entry = q.highest()
        assert entry is not None
        assert entry.level == PriorityLevel.CRITICAL

    def test_highest_empty_queue_returns_none(self):
        q = self._make()
        assert q.highest() is None

    def test_str_entry_with_label(self):
        entry = PriorityEntry("* * * * *", PriorityLevel.HIGH, label="test")
        assert "test" in str(entry)
        assert "High" in str(entry)
