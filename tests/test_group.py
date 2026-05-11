"""Tests for cronparse.group and cronparse.group_export."""
import pytest

from cronparse.exceptions import CronParseError
from cronparse.group import CronGroup, GroupEntry, GroupRegistry
from cronparse.group_export import from_json, to_json


class TestGroupRegistry:
    def _make(self) -> GroupRegistry:
        return GroupRegistry()

    def test_create_returns_cron_group(self):
        reg = self._make()
        g = reg.create("nightly")
        assert isinstance(g, CronGroup)

    def test_create_stores_group(self):
        reg = self._make()
        reg.create("nightly")
        assert reg.get("nightly") is not None

    def test_create_duplicate_raises(self):
        reg = self._make()
        reg.create("nightly")
        with pytest.raises(ValueError, match="already exists"):
            reg.create("nightly")

    def test_create_empty_name_raises(self):
        reg = self._make()
        with pytest.raises(ValueError):
            reg.create("   ")

    def test_get_unknown_returns_none(self):
        reg = self._make()
        assert reg.get("missing") is None

    def test_delete_existing_returns_true(self):
        reg = self._make()
        reg.create("g1")
        assert reg.delete("g1") is True
        assert reg.get("g1") is None

    def test_delete_missing_returns_false(self):
        reg = self._make()
        assert reg.delete("ghost") is False

    def test_names_returns_all_group_names(self):
        reg = self._make()
        reg.create("a")
        reg.create("b")
        assert set(reg.names()) == {"a", "b"}


class TestCronGroup:
    def _make(self, name: str = "test") -> CronGroup:
        reg = GroupRegistry()
        return reg.create(name)

    def test_add_returns_group_entry(self):
        g = self._make()
        entry = g.add("* * * * *")
        assert isinstance(entry, GroupEntry)

    def test_add_stores_entry(self):
        g = self._make()
        g.add("0 * * * *")
        assert len(g) == 1

    def test_add_with_label(self):
        g = self._make()
        entry = g.add("0 9 * * 1", label="Weekly Monday")
        assert entry.label == "Weekly Monday"

    def test_add_invalid_expression_raises(self):
        g = self._make()
        with pytest.raises(CronParseError):
            g.add("not a cron")

    def test_remove_existing_returns_true(self):
        g = self._make()
        g.add("* * * * *")
        assert g.remove("* * * * *") is True
        assert len(g) == 0

    def test_remove_missing_returns_false(self):
        g = self._make()
        assert g.remove("0 0 * * *") is False

    def test_expressions_returns_list(self):
        g = self._make()
        g.add("* * * * *")
        g.add("0 0 * * *")
        assert "* * * * *" in g.expressions()

    def test_str_includes_name(self):
        g = self._make("mygroup")
        g.add("* * * * *")
        assert "mygroup" in str(g)


class TestGroupExport:
    def _populated(self) -> GroupRegistry:
        reg = GroupRegistry()
        g = reg.create("daily")
        g.add("0 0 * * *", label="midnight")
        g.add("0 12 * * *")
        return reg

    def test_to_json_returns_string(self):
        reg = self._populated()
        assert isinstance(to_json(reg), str)

    def test_roundtrip_preserves_groups(self):
        reg = self._populated()
        restored = from_json(to_json(reg))
        assert "daily" in restored.names()

    def test_roundtrip_preserves_entries(self):
        reg = self._populated()
        restored = from_json(to_json(reg))
        g = restored.get("daily")
        assert g is not None
        assert len(g) == 2

    def test_roundtrip_preserves_labels(self):
        reg = self._populated()
        restored = from_json(to_json(reg))
        g = restored.get("daily")
        labels = [e.label for e in g.entries()]
        assert "midnight" in labels
