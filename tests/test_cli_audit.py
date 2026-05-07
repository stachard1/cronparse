"""Tests for cronparse.cli_audit."""
from __future__ import annotations

import json

import pytest

from cronparse.audit import AuditLog
from cronparse.cli_audit import _run_audit, build_audit_parser


class _Args:
    def __init__(self, json_flag: bool = False, action: str | None = None):
        self.json = json_flag
        self.action = action


def _make_log() -> AuditLog:
    log = AuditLog()
    log.record("* * * * *", "added", label="noisy")
    log.record("0 9 * * 1", "added", label="weekly")
    log.record("* * * * *", "removed")
    return log


class TestCliAudit:
    def test_exits_zero_text(self, capsys):
        log = _make_log()
        code = _run_audit(_Args(), log)
        assert code == 0

    def test_text_output_contains_expression(self, capsys):
        log = _make_log()
        _run_audit(_Args(), log)
        out = capsys.readouterr().out
        assert "* * * * *" in out

    def test_json_flag_produces_valid_json(self, capsys):
        log = _make_log()
        _run_audit(_Args(json_flag=True), log)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_action_filter_limits_output(self, capsys):
        log = _make_log()
        _run_audit(_Args(json_flag=True, action="added"), log)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert len(data) == 2
        assert all(e["action"] == "added" for e in data)

    def test_action_filter_no_match_empty_json(self, capsys):
        log = _make_log()
        _run_audit(_Args(json_flag=True, action="validated"), log)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data == []

    def test_build_parser_returns_parser(self):
        import argparse
        p = build_audit_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_empty_log_text_output(self, capsys):
        log = AuditLog()
        _run_audit(_Args(), log)
        out = capsys.readouterr().out
        assert "no audit events" in out
