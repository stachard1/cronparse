"""Tests for cronparse.reminder_export."""

from __future__ import annotations

import json
from datetime import datetime

from cronparse.reminder import ReminderStore
from cronparse.reminder_export import from_json, to_json, to_text

_EXPR = "0 9 * * 1"
_DUE = datetime(2099, 6, 15, 9, 0, 0)


def _make_store() -> ReminderStore:
    store = ReminderStore()
    store.add(_EXPR, "Weekly deploy", _DUE, label="prod")
    store.add("0 0 1 * *", "Monthly report", datetime(2099, 12, 1, 0, 0, 0))
    return store


class TestReminderExport:
    def test_to_json_returns_string(self):
        store = _make_store()
        assert isinstance(to_json(store), str)

    def test_to_json_is_valid_json(self):
        store = _make_store()
        data = json.loads(to_json(store))
        assert isinstance(data, list)

    def test_to_json_entry_count(self):
        store = _make_store()
        data = json.loads(to_json(store))
        assert len(data) == 2

    def test_to_json_contains_required_keys(self):
        store = _make_store()
        data = json.loads(to_json(store))
        for row in data:
            assert "expression" in row
            assert "message" in row
            assert "due" in row
            assert "label" in row

    def test_to_json_label_defaults_to_empty_string(self):
        store = ReminderStore()
        store.add(_EXPR, "No label", _DUE)
        data = json.loads(to_json(store))
        assert data[0]["label"] == ""

    def test_from_json_round_trip(self):
        store = _make_store()
        raw = to_json(store)
        restored = from_json(raw)
        assert len(restored) == 2

    def test_from_json_preserves_expression(self):
        store = _make_store()
        raw = to_json(store)
        restored = from_json(raw)
        expressions = [r.expression for r in restored.all()]
        assert _EXPR in expressions

    def test_from_json_preserves_label(self):
        store = _make_store()
        raw = to_json(store)
        restored = from_json(raw)
        labels = [r.label for r in restored.all()]
        assert "prod" in labels

    def test_from_json_none_label_when_empty_string(self):
        store = ReminderStore()
        store.add(_EXPR, "No label", _DUE)
        raw = to_json(store)
        restored = from_json(raw)
        assert restored.all()[0].label is None

    def test_to_text_returns_string(self):
        store = _make_store()
        assert isinstance(to_text(store), str)

    def test_to_text_empty_store(self):
        store = ReminderStore()
        assert to_text(store) == "No reminders."

    def test_to_text_contains_messages(self):
        store = _make_store()
        text = to_text(store)
        assert "Weekly deploy" in text
        assert "Monthly report" in text
