"""Tests for cronparse.cooldown and cronparse.cooldown_export."""
import json
import pytest

from cronparse.cooldown import CooldownEntry, CooldownStore
from cronparse.cooldown_export import from_json, to_json, to_text
from cronparse.exceptions import CronParseError


EXPR = "*/5 * * * *"
EXPR2 = "0 * * * *"


class TestCooldownStore:
    def _make(self) -> CooldownStore:
        return CooldownStore()

    def test_add_returns_cooldown_entry(self):
        store = self._make()
        entry = store.add(EXPR, 300)
        assert isinstance(entry, CooldownEntry)

    def test_add_stores_entry(self):
        store = self._make()
        store.add(EXPR, 300)
        assert store.get(EXPR) is not None

    def test_add_with_label(self):
        store = self._make()
        entry = store.add(EXPR, 60, label="  my job  ")
        assert entry.label == "my job"

    def test_add_invalid_expression_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.add("not a cron", 60)

    def test_add_zero_interval_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add(EXPR, 0)

    def test_add_negative_interval_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add(EXPR, -10)

    def test_remove_existing_returns_true(self):
        store = self._make()
        store.add(EXPR, 300)
        assert store.remove(EXPR) is True
        assert store.get(EXPR) is None

    def test_remove_missing_returns_false(self):
        store = self._make()
        assert store.remove(EXPR) is False

    def test_all_returns_list(self):
        store = self._make()
        store.add(EXPR, 300)
        store.add(EXPR2, 3600)
        assert len(store.all()) == 2

    def test_is_allowed_no_rule_always_true(self):
        store = self._make()
        assert store.is_allowed(EXPR, 10) is True

    def test_is_allowed_none_elapsed_always_true(self):
        store = self._make()
        store.add(EXPR, 300)
        assert store.is_allowed(EXPR, None) is True

    def test_is_allowed_sufficient_time(self):
        store = self._make()
        store.add(EXPR, 300)
        assert store.is_allowed(EXPR, 300) is True
        assert store.is_allowed(EXPR, 600) is True

    def test_is_allowed_insufficient_time(self):
        store = self._make()
        store.add(EXPR, 300)
        assert store.is_allowed(EXPR, 299) is False
        assert store.is_allowed(EXPR, 0) is False

    def test_min_interval_timedelta(self):
        store = self._make()
        entry = store.add(EXPR, 120)
        from datetime import timedelta
        assert entry.min_interval == timedelta(seconds=120)


class TestCooldownExport:
    def _make(self) -> CooldownStore:
        store = CooldownStore()
        store.add(EXPR, 300, label="fast job")
        store.add(EXPR2, 3600)
        return store

    def test_to_json_returns_string(self):
        assert isinstance(to_json(self._make()), str)

    def test_to_json_is_valid_json(self):
        data = json.loads(to_json(self._make()))
        assert isinstance(data, list)

    def test_to_json_entry_count(self):
        data = json.loads(to_json(self._make()))
        assert len(data) == 2

    def test_to_json_required_keys(self):
        data = json.loads(to_json(self._make()))
        for row in data:
            assert "expression" in row
            assert "min_interval_seconds" in row
            assert "label" in row

    def test_round_trip(self):
        original = self._make()
        restored = from_json(to_json(original))
        assert len(restored.all()) == len(original.all())
        e = restored.get(EXPR)
        assert e is not None
        assert e.min_interval_seconds == 300
        assert e.label == "fast job"

    def test_to_text_contains_expression(self):
        text = to_text(self._make())
        assert EXPR in text

    def test_to_text_empty_store(self):
        text = to_text(CooldownStore())
        assert "No cooldown" in text
