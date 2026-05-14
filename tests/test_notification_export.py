"""Tests for cronparse.notification_export."""
import json
import pytest

from cronparse.notification import NotificationStore
from cronparse.notification_export import to_json, from_json, to_text


def _make_store() -> NotificationStore:
    store = NotificationStore()
    store.add("* * * * *", "email", label="every-minute")
    store.add("0 9 * * 1-5", "slack", label="weekday-morning")
    store.add("0 0 1 * *", "webhook", enabled=False)
    return store


class TestNotificationExport:
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
        assert len(data) == 3

    def test_to_json_contains_required_keys(self):
        store = _make_store()
        data = json.loads(to_json(store))
        for entry in data:
            assert "expression" in entry
            assert "channel" in entry
            assert "enabled" in entry

    def test_to_json_preserves_label(self):
        store = _make_store()
        data = json.loads(to_json(store))
        assert data[0]["label"] == "every-minute"

    def test_to_json_preserves_enabled_false(self):
        store = _make_store()
        data = json.loads(to_json(store))
        assert data[2]["enabled"] is False

    def test_from_json_round_trips(self):
        store = _make_store()
        raw = to_json(store)
        restored = from_json(raw)
        original_rules = store.all()
        restored_rules = restored.all()
        assert len(restored_rules) == len(original_rules)
        for orig, rest in zip(original_rules, restored_rules):
            assert orig.expression == rest.expression
            assert orig.channel == rest.channel
            assert orig.enabled == rest.enabled

    def test_from_json_missing_label_defaults_none(self):
        raw = json.dumps([{"expression": "* * * * *", "channel": "email", "enabled": True}])
        store = from_json(raw)
        assert store.all()[0].label is None

    def test_to_text_returns_string(self):
        store = _make_store()
        assert isinstance(to_text(store), str)

    def test_to_text_empty_store(self):
        store = NotificationStore()
        assert "No notification rules" in to_text(store)

    def test_to_text_contains_channels(self):
        store = _make_store()
        text = to_text(store)
        assert "email" in text
        assert "slack" in text
