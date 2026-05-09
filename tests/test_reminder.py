"""Tests for cronparse.reminder."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta

from cronparse.reminder import Reminder, ReminderStore
from cronparse.exceptions import CronParseError

_EXPR = "0 9 * * 1"  # every Monday at 09:00
_FUTURE = datetime(2099, 1, 1, 0, 0, 0)
_PAST = datetime(2000, 1, 1, 0, 0, 0)
_NOW = datetime(2024, 6, 15, 12, 0, 0)


class TestReminderStore:
    def _make(self) -> ReminderStore:
        return ReminderStore()

    def test_add_returns_reminder_instance(self):
        store = self._make()
        r = store.add(_EXPR, "Deploy release", _FUTURE)
        assert isinstance(r, Reminder)

    def test_add_stores_entry(self):
        store = self._make()
        store.add(_EXPR, "Deploy release", _FUTURE)
        assert len(store) == 1

    def test_add_with_label(self):
        store = self._make()
        r = store.add(_EXPR, "Deploy release", _FUTURE, label="prod")
        assert r.label == "prod"

    def test_add_strips_label_whitespace(self):
        store = self._make()
        r = store.add(_EXPR, "Deploy", _FUTURE, label="  prod  ")
        assert r.label == "prod"

    def test_add_invalid_expression_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.add("not a cron", "msg", _FUTURE)

    def test_add_empty_message_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add(_EXPR, "   ", _FUTURE)

    def test_all_returns_copy(self):
        store = self._make()
        store.add(_EXPR, "msg", _FUTURE)
        result = store.all()
        result.clear()
        assert len(store) == 1

    def test_remove_existing_entry(self):
        store = self._make()
        r = store.add(_EXPR, "msg", _FUTURE)
        assert store.remove(r) is True
        assert len(store) == 0

    def test_remove_nonexistent_returns_false(self):
        store = self._make()
        r = Reminder(_EXPR, "msg", _FUTURE)
        assert store.remove(r) is False

    def test_overdue_returns_past_reminders(self):
        store = self._make()
        store.add(_EXPR, "old", _PAST)
        store.add(_EXPR, "future", _FUTURE)
        overdue = store.overdue(now=_NOW)
        assert len(overdue) == 1
        assert overdue[0].message == "old"

    def test_for_expression_filters_correctly(self):
        store = self._make()
        store.add(_EXPR, "msg1", _FUTURE)
        store.add("* * * * *", "msg2", _FUTURE)
        result = store.for_expression(_EXPR)
        assert len(result) == 1
        assert result[0].message == "msg1"

    def test_is_overdue_true_when_past(self):
        r = Reminder(_EXPR, "msg", _PAST)
        assert r.is_overdue(now=_NOW) is True

    def test_is_overdue_false_when_future(self):
        r = Reminder(_EXPR, "msg", _FUTURE)
        assert r.is_overdue(now=_NOW) is False

    def test_str_includes_expression_and_message(self):
        r = Reminder(_EXPR, "Deploy", _FUTURE, label="prod")
        s = str(r)
        assert _EXPR in s
        assert "Deploy" in s
        assert "prod" in s
