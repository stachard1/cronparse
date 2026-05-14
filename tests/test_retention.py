"""Tests for cronparse.retention and cronparse.retention_export."""
from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from cronparse.history import CronHistory
from cronparse.retention import (
    RetentionPolicy,
    RetentionResult,
    apply_retention,
)
from cronparse.retention_export import from_json, to_json, to_text


def _make(expressions=None) -> CronHistory:
    h = CronHistory()
    for expr in expressions or ["* * * * *", "0 * * * *", "0 0 * * *"]:
        h.add(expr)
    return h


class TestRetentionPolicy:
    def test_str_unbounded(self):
        assert "keep=all" in str(RetentionPolicy())

    def test_str_with_max_entries(self):
        assert "max_entries=5" in str(RetentionPolicy(max_entries=5))

    def test_str_with_max_age(self):
        assert "max_age_days=7" in str(RetentionPolicy(max_age_days=7))

    def test_is_unbounded_true(self):
        assert RetentionPolicy().is_unbounded is True

    def test_is_unbounded_false_when_entries_set(self):
        assert RetentionPolicy(max_entries=1).is_unbounded is False


class TestApplyRetention:
    def test_returns_retention_result(self):
        h = _make()
        result = apply_retention(h, RetentionPolicy())
        assert isinstance(result, RetentionResult)

    def test_unbounded_keeps_all(self):
        h = _make()
        result = apply_retention(h, RetentionPolicy())
        assert result.removed_count == 0
        assert result.kept_count == 3

    def test_max_entries_removes_oldest(self):
        h = _make(["* * * * *", "0 * * * *", "0 0 * * *"])
        result = apply_retention(h, RetentionPolicy(max_entries=2))
        assert result.removed_count == 1
        assert result.kept_count == 2

    def test_max_entries_no_removal_when_under_limit(self):
        h = _make(["* * * * *", "0 * * * *"])
        result = apply_retention(h, RetentionPolicy(max_entries=5))
        assert result.removed_count == 0

    def test_max_age_removes_old_entries(self):
        h = CronHistory()
        h.add("* * * * *")
        # Manually backdate the first entry
        h.entries[0].added_at = datetime.utcnow() - timedelta(days=10)
        h.add("0 * * * *")
        result = apply_retention(h, RetentionPolicy(max_age_days=5))
        assert result.removed_count == 1
        assert result.kept_count == 1

    def test_str_representation(self):
        r = RetentionResult(removed=[], kept=[])
        assert "RetentionResult" in str(r)


class TestRetentionExport:
    def _policies(self):
        return [
            RetentionPolicy(max_entries=10, label="short"),
            RetentionPolicy(max_age_days=30.0, label="monthly"),
        ]

    def test_to_json_returns_string(self):
        assert isinstance(to_json(self._policies()), str)

    def test_to_json_is_valid_json(self):
        parsed = json.loads(to_json(self._policies()))
        assert isinstance(parsed, list)

    def test_roundtrip(self):
        policies = self._policies()
        restored = from_json(to_json(policies))
        assert len(restored) == len(policies)
        assert restored[0].max_entries == 10
        assert restored[1].max_age_days == 30.0

    def test_to_text_no_policies(self):
        assert "No retention" in to_text([])

    def test_to_text_lists_policies(self):
        text = to_text(self._policies())
        assert "short" in text
        assert "monthly" in text
