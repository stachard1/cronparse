"""Tests for cronparse.alias and cronparse.alias_export."""

import json
import pytest

from cronparse.alias import AliasEntry, AliasRegistry
from cronparse.alias_export import from_json, to_json
from cronparse.exceptions import CronParseError


class TestAliasRegistry:
    def _make(self) -> AliasRegistry:
        return AliasRegistry()

    def test_register_returns_alias_entry(self):
        reg = self._make()
        entry = reg.register("hourly", "0 * * * *")
        assert isinstance(entry, AliasEntry)

    def test_register_stores_entry(self):
        reg = self._make()
        reg.register("hourly", "0 * * * *", "Every hour")
        assert reg.get("hourly") is not None

    def test_register_invalid_expression_raises(self):
        reg = self._make()
        with pytest.raises(CronParseError):
            reg.register("bad", "99 99 99 99 99")

    def test_register_empty_name_raises(self):
        reg = self._make()
        with pytest.raises(ValueError):
            reg.register("", "* * * * *")

    def test_get_unknown_returns_none(self):
        reg = self._make()
        assert reg.get("missing") is None

    def test_remove_existing_returns_true(self):
        reg = self._make()
        reg.register("hourly", "0 * * * *")
        assert reg.remove("hourly") is True
        assert reg.get("hourly") is None

    def test_remove_missing_returns_false(self):
        reg = self._make()
        assert reg.remove("nope") is False

    def test_all_returns_sorted_list(self):
        reg = self._make()
        reg.register("zebra", "* * * * *")
        reg.register("alpha", "0 * * * *")
        names = [e.name for e in reg.all()]
        assert names == sorted(names)

    def test_len_reflects_count(self):
        reg = self._make()
        reg.register("a", "* * * * *")
        reg.register("b", "0 * * * *")
        assert len(reg) == 2

    def test_str_includes_name_and_expression(self):
        reg = self._make()
        entry = reg.register("daily", "0 0 * * *", "Midnight daily")
        text = str(entry)
        assert "daily" in text
        assert "0 0 * * *" in text


class TestAliasExport:
    def _make(self) -> AliasRegistry:
        reg = AliasRegistry()
        reg.register("hourly", "0 * * * *", "Every hour")
        reg.register("daily", "0 0 * * *", "Midnight")
        return reg

    def test_to_json_returns_string(self):
        assert isinstance(to_json(self._make()), str)

    def test_to_json_is_valid_json(self):
        raw = to_json(self._make())
        parsed = json.loads(raw)
        assert isinstance(parsed, list)

    def test_to_json_entry_count(self):
        raw = to_json(self._make())
        assert len(json.loads(raw)) == 2

    def test_round_trip_preserves_data(self):
        original = self._make()
        restored = from_json(to_json(original))
        assert len(restored) == len(original)
        entry = restored.get("hourly")
        assert entry is not None
        assert entry.expression == "0 * * * *"
        assert entry.description == "Every hour"

    def test_from_json_empty_list(self):
        reg = from_json("[]")
        assert len(reg) == 0
