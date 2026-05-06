"""Tests for cronparse.history module."""

import pytest
from cronparse.history import CronHistory
from cronparse.exceptions import CronParseError


class TestCronHistory:
    def test_add_valid_expression(self):
        h = CronHistory()
        entry = h.add("* * * * *")
        assert entry.expression == "* * * * *"
        assert len(h) == 1

    def test_add_with_label(self):
        h = CronHistory()
        entry = h.add("0 9 * * 1", label="Weekly Monday")
        assert entry.label == "Weekly Monday"

    def test_add_invalid_expression_raises(self):
        h = CronHistory()
        with pytest.raises(Exception):
            h.add("not a cron")

    def test_add_multiple_entries(self):
        h = CronHistory()
        h.add("* * * * *")
        h.add("0 0 * * *")
        assert len(h) == 2

    def test_remove_existing_expression(self):
        h = CronHistory()
        h.add("* * * * *")
        removed = h.remove("* * * * *")
        assert removed == 1
        assert len(h) == 0

    def test_remove_nonexistent_expression(self):
        h = CronHistory()
        removed = h.remove("0 0 * * *")
        assert removed == 0

    def test_find_returns_matching_entries(self):
        h = CronHistory()
        h.add("* * * * *", label="first")
        h.add("0 0 * * *")
        h.add("* * * * *", label="second")
        results = h.find("* * * * *")
        assert len(results) == 2

    def test_find_returns_empty_when_no_match(self):
        h = CronHistory()
        h.add("* * * * *")
        assert h.find("0 0 * * *") == []

    def test_clear_removes_all(self):
        h = CronHistory()
        h.add("* * * * *")
        h.add("0 0 * * *")
        h.clear()
        assert len(h) == 0

    def test_iter_yields_entries(self):
        h = CronHistory()
        h.add("* * * * *")
        h.add("0 0 * * *")
        expressions = [e.expression for e in h]
        assert "* * * * *" in expressions
        assert "0 0 * * *" in expressions

    def test_entry_str_without_label(self):
        h = CronHistory()
        entry = h.add("* * * * *")
        assert "* * * * *" in str(entry)
        assert "(" not in str(entry)

    def test_entry_str_with_label(self):
        h = CronHistory()
        entry = h.add("* * * * *", label="All stars")
        assert "All stars" in str(entry)
