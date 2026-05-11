"""Tests for cronparse.cli_group."""
import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from cronparse.cli_group import _run_group
from cronparse.group import GroupRegistry


class _Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestCliGroup:
    def _make(self) -> GroupRegistry:
        return GroupRegistry()

    def test_create_exits_zero(self, capsys):
        reg = self._make()
        args = _Args(group_cmd="create", name="nightly")
        code = _run_group(args, reg)
        assert code == 0

    def test_create_prints_confirmation(self, capsys):
        reg = self._make()
        args = _Args(group_cmd="create", name="nightly")
        _run_group(args, reg)
        out = capsys.readouterr().out
        assert "nightly" in out

    def test_create_duplicate_exits_one(self, capsys):
        reg = self._make()
        reg.create("nightly")
        args = _Args(group_cmd="create", name="nightly")
        code = _run_group(args, reg)
        assert code == 1

    def test_add_exits_zero(self, capsys):
        reg = self._make()
        reg.create("g")
        args = _Args(group_cmd="add", name="g", expression="* * * * *", label=None)
        code = _run_group(args, reg)
        assert code == 0

    def test_add_missing_group_exits_one(self, capsys):
        reg = self._make()
        args = _Args(group_cmd="add", name="ghost", expression="* * * * *", label=None)
        code = _run_group(args, reg)
        assert code == 1

    def test_add_invalid_expression_exits_one(self, capsys):
        reg = self._make()
        reg.create("g")
        args = _Args(group_cmd="add", name="g", expression="bad expr", label=None)
        code = _run_group(args, reg)
        assert code == 1

    def test_list_all_groups(self, capsys):
        reg = self._make()
        reg.create("a")
        reg.create("b")
        args = _Args(group_cmd="list", name=None)
        _run_group(args, reg)
        out = capsys.readouterr().out
        assert "a" in out and "b" in out

    def test_list_specific_group(self, capsys):
        reg = self._make()
        g = reg.create("mygroup")
        g.add("0 0 * * *", label="midnight")
        args = _Args(group_cmd="list", name="mygroup")
        _run_group(args, reg)
        out = capsys.readouterr().out
        assert "mygroup" in out

    def test_list_missing_group_exits_one(self, capsys):
        reg = self._make()
        args = _Args(group_cmd="list", name="ghost")
        code = _run_group(args, reg)
        assert code == 1

    def test_export_produces_valid_json(self, capsys):
        reg = self._make()
        g = reg.create("daily")
        g.add("0 0 * * *")
        args = _Args(group_cmd="export")
        _run_group(args, reg)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert data[0]["name"] == "daily"
