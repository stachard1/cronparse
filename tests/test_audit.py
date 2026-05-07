"""Tests for cronparse.audit and cronparse.audit_export."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from cronparse.audit import AuditEvent, AuditLog
from cronparse.audit_export import from_json, to_json, to_text


class TestAuditLog:
    def _make(self) -> AuditLog:
        log = AuditLog()
        log.record("* * * * *", "added", label="every-minute")
        log.record("0 9 * * 1", "added", label="weekly")
        log.record("* * * * *", "removed", note="too noisy")
        return log

    def test_record_appends_event(self):
        log = AuditLog()
        event = log.record("* * * * *", "added")
        assert isinstance(event, AuditEvent)
        assert len(log) == 1

    def test_events_returns_copy(self):
        log = self._make()
        events = log.events()
        events.clear()
        assert len(log) == 3  # original unaffected

    def test_filter_by_action(self):
        log = self._make()
        added = log.filter_by_action("added")
        assert len(added) == 2
        assert all(e.action == "added" for e in added)

    def test_filter_by_action_case_insensitive(self):
        log = self._make()
        assert len(log.filter_by_action("ADDED")) == 2

    def test_filter_by_expression(self):
        log = self._make()
        results = log.filter_by_expression("* * * * *")
        assert len(results) == 2

    def test_clear_empties_log(self):
        log = self._make()
        log.clear()
        assert len(log) == 0

    def test_str_contains_action_and_expression(self):
        log = AuditLog()
        event = log.record("0 0 * * *", "validated", label="midnight")
        text = str(event)
        assert "VALIDATED" in text
        assert "0 0 * * *" in text
        assert "midnight" in text


class TestAuditExport:
    def _make_log(self) -> AuditLog:
        log = AuditLog()
        log.record("*/5 * * * *", "added", label="every-5-min")
        log.record("0 12 * * *", "updated", note="changed from 11")
        return log

    def test_to_json_returns_string(self):
        log = self._make_log()
        result = to_json(log)
        assert isinstance(result, str)

    def test_to_json_valid_structure(self):
        log = self._make_log()
        data = json.loads(to_json(log))
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["expression"] == "*/5 * * * *"
        assert data[0]["action"] == "added"

    def test_from_json_roundtrip(self):
        log = self._make_log()
        restored = from_json(to_json(log))
        assert len(restored) == len(log)
        for orig, copy in zip(log.events(), restored.events()):
            assert orig.expression == copy.expression
            assert orig.action == copy.action
            assert orig.label == copy.label

    def test_to_text_contains_events(self):
        log = self._make_log()
        text = to_text(log)
        assert "*/5 * * * *" in text
        assert "0 12 * * *" in text

    def test_to_text_empty_log(self):
        log = AuditLog()
        assert "no audit events" in to_text(log)
