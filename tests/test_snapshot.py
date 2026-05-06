"""Tests for cronparse.snapshot module."""

import json
from datetime import datetime

import pytest
from cronparse.history import CronHistory, HistoryEntry
from cronparse.snapshot import dump, load, to_json, from_json, DATETIME_FMT


class TestSnapshot:
    def _make_history(self) -> CronHistory:
        h = CronHistory()
        h.add("* * * * *", label="every minute")
        h.add("0 0 * * *")
        return h

    def test_dump_returns_list_of_dicts(self):
        h = self._make_history()
        result = dump(h)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_dump_contains_required_keys(self):
        h = self._make_history()
        result = dump(h)
        for item in result:
            assert "expression" in item
            assert "label" in item
            assert "added_at" in item

    def test_dump_preserves_label(self):
        h = self._make_history()
        result = dump(h)
        assert result[0]["label"] == "every minute"
        assert result[1]["label"] is None

    def test_load_restores_history(self):
        h = self._make_history()
        data = dump(h)
        restored = load(data)
        assert len(restored) == 2
        assert restored.entries[0].expression == "* * * * *"

    def test_load_skips_invalid_entries(self):
        data = [
            {"expression": "* * * * *", "label": None, "added_at": "2024-01-01T00:00:00"},
            {"bad": "entry"},
        ]
        restored = load(data)
        assert len(restored) == 1

    def test_to_json_produces_valid_json(self):
        h = self._make_history()
        raw = to_json(h)
        parsed = json.loads(raw)
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_from_json_restores_history(self):
        h = self._make_history()
        raw = to_json(h)
        restored = from_json(raw)
        assert len(restored) == 2
        expressions = [e.expression for e in restored]
        assert "* * * * *" in expressions
        assert "0 0 * * *" in expressions

    def test_roundtrip_preserves_labels(self):
        h = self._make_history()
        raw = to_json(h)
        restored = from_json(raw)
        assert restored.entries[0].label == "every minute"

    def test_roundtrip_preserves_added_at(self):
        h = CronHistory()
        fixed_time = datetime(2024, 6, 15, 12, 0, 0)
        entry = HistoryEntry(expression="* * * * *", label=None, added_at=fixed_time)
        h.entries.append(entry)
        raw = to_json(h)
        restored = from_json(raw)
        assert restored.entries[0].added_at == fixed_time
