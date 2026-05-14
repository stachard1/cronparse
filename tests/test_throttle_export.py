"""Tests for cronparse.throttle_export."""
import json

import pytest

from cronparse.throttle import ThrottleStore
from cronparse.throttle_export import from_json, to_json, to_text


def _make_store() -> ThrottleStore:
    store = ThrottleStore()
    store.add("* * * * *", max_runs=5, window_seconds=300, label="every-minute")
    store.add("0 * * * *", max_runs=1, window_seconds=3600, label="hourly")
    return store


class TestThrottleExport:
    def test_to_json_returns_string(self):
        store = _make_store()
        assert isinstance(to_json(store), str)

    def test_to_json_is_valid_json(self):
        store = _make_store()
        parsed = json.loads(to_json(store))
        assert isinstance(parsed, list)

    def test_to_json_entry_count(self):
        store = _make_store()
        parsed = json.loads(to_json(store))
        assert len(parsed) == 2

    def test_to_json_contains_required_keys(self):
        store = _make_store()
        parsed = json.loads(to_json(store))
        for entry in parsed:
            assert "expression" in entry
            assert "max_runs" in entry
            assert "window_seconds" in entry
            assert "label" in entry

    def test_from_json_roundtrip(self):
        store = _make_store()
        raw = to_json(store)
        restored = from_json(raw)
        assert len(restored.all()) == 2

    def test_from_json_preserves_max_runs(self):
        store = _make_store()
        raw = to_json(store)
        restored = from_json(raw)
        rule = restored.get("* * * * *")
        assert rule is not None
        assert rule.max_runs == 5

    def test_from_json_preserves_label(self):
        store = _make_store()
        raw = to_json(store)
        restored = from_json(raw)
        rule = restored.get("0 * * * *")
        assert rule is not None
        assert rule.label == "hourly"

    def test_from_json_missing_label_defaults_empty(self):
        data = json.dumps([{"expression": "* * * * *", "max_runs": 1, "window_seconds": 60}])
        store = from_json(data)
        rule = store.get("* * * * *")
        assert rule is not None
        assert rule.label == ""

    def test_to_text_returns_string(self):
        store = _make_store()
        assert isinstance(to_text(store), str)

    def test_to_text_empty_store(self):
        store = ThrottleStore()
        assert "No throttle rules" in to_text(store)

    def test_to_text_contains_labels(self):
        store = _make_store()
        text = to_text(store)
        assert "every-minute" in text
        assert "hourly" in text
