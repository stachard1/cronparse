"""Tests for cronparse.tags.TagIndex."""

import pytest

from cronparse.exceptions import CronParseError
from cronparse.tags import TagIndex


class TestTagIndex:
    def _make(self) -> TagIndex:
        return TagIndex()

    def test_add_and_get(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        assert "0 9 * * *" in idx.get("daily")

    def test_add_normalises_tag_case(self):
        idx = self._make()
        idx.add("Daily", "0 9 * * *")
        assert idx.get("daily") == ["0 9 * * *"]

    def test_add_empty_tag_raises(self):
        idx = self._make()
        with pytest.raises(CronParseError):
            idx.add("", "0 9 * * *")

    def test_add_duplicate_expression_ignored(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        idx.add("daily", "0 9 * * *")
        assert idx.get("daily").count("0 9 * * *") == 1

    def test_remove_entire_tag(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        idx.remove("daily")
        assert idx.get("daily") == []

    def test_remove_single_expression_from_tag(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        idx.add("daily", "0 10 * * *")
        idx.remove("daily", "0 9 * * *")
        assert idx.get("daily") == ["0 10 * * *"]

    def test_remove_last_expression_removes_tag(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        idx.remove("daily", "0 9 * * *")
        assert "daily" not in idx.all_tags()

    def test_remove_nonexistent_tag_is_safe(self):
        idx = self._make()
        idx.remove("ghost")

    def test_tags_for_expression(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        idx.add("morning", "0 9 * * *")
        tags = idx.tags_for("0 9 * * *")
        assert set(tags) == {"daily", "morning"}

    def test_all_tags(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        idx.add("weekly", "0 9 * * 1")
        assert set(idx.all_tags()) == {"daily", "weekly"}

    def test_to_dict_and_from_dict_roundtrip(self):
        idx = self._make()
        idx.add("daily", "0 9 * * *")
        idx.add("morning", "0 9 * * *")
        idx.add("weekly", "0 9 * * 1")
        data = idx.to_dict()
        restored = TagIndex.from_dict(data)
        assert set(restored.all_tags()) == {"daily", "morning", "weekly"}
        assert "0 9 * * *" in restored.get("daily")
