"""Tests for cronparse.priority_export."""
import json

from cronparse.priority import PriorityLevel, PriorityQueue
from cronparse.priority_export import from_json, to_json, to_text


def _make_queue() -> PriorityQueue:
    q = PriorityQueue()
    q.add("* * * * *", level=PriorityLevel.NORMAL, label="every minute")
    q.add("0 * * * *", level=PriorityLevel.HIGH, label="hourly")
    return q


class TestPriorityExport:
    def test_to_json_returns_string(self):
        q = _make_queue()
        assert isinstance(to_json(q), str)

    def test_to_json_is_valid_json(self):
        q = _make_queue()
        parsed = json.loads(to_json(q))
        assert isinstance(parsed, list)

    def test_to_json_entry_count(self):
        q = _make_queue()
        parsed = json.loads(to_json(q))
        assert len(parsed) == 2

    def test_to_json_contains_required_keys(self):
        q = _make_queue()
        parsed = json.loads(to_json(q))
        for item in parsed:
            assert "expression" in item
            assert "level" in item
            assert "label" in item

    def test_from_json_roundtrip(self):
        q = _make_queue()
        raw = to_json(q)
        restored = from_json(raw)
        assert len(restored) == len(q)

    def test_from_json_preserves_level(self):
        q = _make_queue()
        raw = to_json(q)
        restored = from_json(raw)
        levels = {e.expression: e.level for e in restored.get()}
        assert levels["0 * * * *"] == PriorityLevel.HIGH

    def test_from_json_preserves_label(self):
        q = _make_queue()
        raw = to_json(q)
        restored = from_json(raw)
        labels = {e.expression: e.label for e in restored.get()}
        assert labels["* * * * *"] == "every minute"

    def test_to_text_returns_string(self):
        q = _make_queue()
        assert isinstance(to_text(q), str)

    def test_to_text_empty_queue(self):
        q = PriorityQueue()
        assert to_text(q) == "No entries."

    def test_to_text_contains_expressions(self):
        q = _make_queue()
        text = to_text(q)
        assert "* * * * *" in text
        assert "0 * * * *" in text
