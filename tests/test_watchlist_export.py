"""Tests for cronparse.watchlist_export."""
import json
import pytest

from cronparse.watchlist import Watchlist
from cronparse.watchlist_export import to_json, from_json


def _make_watchlist() -> Watchlist:
    wl = Watchlist()
    wl.add("* * * * *", "every-minute")
    wl.add("0 9 * * 1-5", "weekday-morning")
    return wl


class TestWatchlistExport:
    def test_to_json_returns_string(self):
        wl = _make_watchlist()
        result = to_json(wl)
        assert isinstance(result, str)

    def test_to_json_is_valid_json(self):
        wl = _make_watchlist()
        parsed = json.loads(to_json(wl))
        assert isinstance(parsed, list)

    def test_to_json_entry_count(self):
        wl = _make_watchlist()
        parsed = json.loads(to_json(wl))
        assert len(parsed) == 2

    def test_to_json_contains_required_keys(self):
        wl = _make_watchlist()
        parsed = json.loads(to_json(wl))
        for item in parsed:
            assert "expression" in item
            assert "label" in item
            assert "added_at" in item
            assert "last_changed" in item

    def test_to_json_last_changed_none_by_default(self):
        wl = _make_watchlist()
        parsed = json.loads(to_json(wl))
        for item in parsed:
            assert item["last_changed"] is None

    def test_to_json_last_changed_set_after_update(self):
        wl = Watchlist()
        wl.add("* * * * *", "job")
        wl.update("job", "0 0 * * *")
        parsed = json.loads(to_json(wl))
        assert parsed[0]["last_changed"] is not None

    def test_round_trip_preserves_expressions(self):
        wl = _make_watchlist()
        restored = from_json(to_json(wl))
        original_exprs = {e.expression for e in wl.all()}
        restored_exprs = {e.expression for e in restored.all()}
        assert original_exprs == restored_exprs

    def test_round_trip_preserves_labels(self):
        wl = _make_watchlist()
        restored = from_json(to_json(wl))
        assert restored.get("every-minute") is not None
        assert restored.get("weekday-morning") is not None

    def test_round_trip_empty_watchlist(self):
        wl = Watchlist()
        restored = from_json(to_json(wl))
        assert len(restored) == 0

    def test_from_json_invalid_raises(self):
        with pytest.raises(Exception):
            from_json("not json at all")
