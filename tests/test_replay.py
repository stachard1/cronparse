"""Tests for cronparse.replay and cronparse.replay_export."""

from __future__ import annotations

from datetime import datetime

import pytest

from cronparse.replay import ReplayEntry, ReplayResult, replay
from cronparse.replay_export import from_json, to_json, to_text


class TestReplay:
    _start = datetime(2024, 1, 1, 0, 0)
    _end = datetime(2024, 1, 1, 0, 5)

    def test_returns_replay_result_instance(self):
        result = replay("* * * * *", self._start, self._end)
        assert isinstance(result, ReplayResult)

    def test_every_minute_fires_six_times_in_five_minute_window(self):
        result = replay("* * * * *", self._start, self._end)
        assert result.count == 6

    def test_entries_are_replay_entry_instances(self):
        result = replay("* * * * *", self._start, self._end)
        assert all(isinstance(e, ReplayEntry) for e in result.entries)

    def test_specific_minute_fires_once(self):
        result = replay("3 0 1 1 *", self._start, self._end)
        assert result.count == 1
        assert result.entries[0].fired_at == datetime(2024, 1, 1, 0, 3)

    def test_no_match_returns_empty_entries(self):
        result = replay("0 12 1 1 *", self._start, self._end)
        assert result.count == 0
        assert result.entries == []

    def test_invalid_expression_returns_empty_result(self):
        result = replay("invalid", self._start, self._end)
        assert result.count == 0

    def test_label_is_preserved(self):
        result = replay("* * * * *", self._start, self._end, label="my-job")
        assert result.label == "my-job"
        assert all(e.label == "my-job" for e in result.entries)

    def test_max_entries_respected(self):
        start = datetime(2024, 1, 1, 0, 0)
        end = datetime(2024, 1, 1, 1, 0)  # 61 minutes
        result = replay("* * * * *", start, end, max_entries=10)
        assert result.count == 10

    def test_str_contains_expression(self):
        result = replay("0 * * * *", self._start, self._end)
        assert "0 * * * *" in str(result)

    def test_entry_str_contains_timestamp(self):
        result = replay("3 0 1 1 *", self._start, self._end)
        assert "2024-01-01 00:03" in str(result.entries[0])


class TestReplayExport:
    _start = datetime(2024, 6, 1, 9, 0)
    _end = datetime(2024, 6, 1, 9, 3)

    def _make(self, expression="* * * * *", label=None):
        return replay(expression, self._start, self._end, label=label)

    def test_to_json_returns_string(self):
        assert isinstance(to_json(self._make()), str)

    def test_to_json_roundtrip_preserves_count(self):
        original = self._make()
        restored = from_json(to_json(original))
        assert restored.count == original.count

    def test_to_json_roundtrip_preserves_label(self):
        original = self._make(label="backup")
        restored = from_json(to_json(original))
        assert restored.label == "backup"

    def test_to_json_roundtrip_preserves_fired_at(self):
        original = self._make()
        restored = from_json(to_json(original))
        assert restored.entries[0].fired_at == original.entries[0].fired_at

    def test_to_text_returns_string(self):
        assert isinstance(to_text(self._make()), str)

    def test_to_text_contains_expression(self):
        result = to_text(self._make())
        assert "* * * * *" in result
