"""Tests for cronparse.quota_export."""
from __future__ import annotations

import json

import pytest

from cronparse.quota import QuotaStore
from cronparse.quota_export import from_json, to_json, to_text

EXPR = "0 * * * *"
EXPR2 = "30 6 * * 1"


def _make_store() -> QuotaStore:
    store = QuotaStore()
    store.add(EXPR, max_runs=10, window_hours=2, label="hourly")
    store.add(EXPR2, max_runs=1, window_hours=24, label="weekly")
    return store


class TestQuotaExport:
    def test_to_json_returns_string(self):
        assert isinstance(to_json(_make_store()), str)

    def test_to_json_is_valid_json(self):
        data = json.loads(to_json(_make_store()))
        assert isinstance(data, list)

    def test_to_json_entry_count(self):
        data = json.loads(to_json(_make_store()))
        assert len(data) == 2

    def test_to_json_contains_required_keys(self):
        data = json.loads(to_json(_make_store()))
        for item in data:
            assert "expression" in item
            assert "max_runs" in item
            assert "window_hours" in item
            assert "label" in item

    def test_to_json_preserves_values(self):
        data = json.loads(to_json(_make_store()))
        first = data[0]
        assert first["expression"] == EXPR
        assert first["max_runs"] == 10
        assert first["window_hours"] == 2
        assert first["label"] == "hourly"

    def test_from_json_round_trip(self):
        original = _make_store()
        restored = from_json(to_json(original))
        assert len(restored.all()) == 2
        entry = restored.get(EXPR)
        assert entry is not None
        assert entry.max_runs == 10
        assert entry.window_hours == 2
        assert entry.label == "hourly"

    def test_from_json_missing_label_defaults_empty(self):
        raw = json.dumps([{"expression": EXPR, "max_runs": 5, "window_hours": 1}])
        store = from_json(raw)
        entry = store.get(EXPR)
        assert entry is not None
        assert entry.label == ""

    def test_to_text_returns_string(self):
        assert isinstance(to_text(_make_store()), str)

    def test_to_text_contains_expression(self):
        text = to_text(_make_store())
        assert EXPR in text

    def test_to_text_empty_store(self):
        store = QuotaStore()
        assert to_text(store) == "No quota entries defined."
