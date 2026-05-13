"""Tests for cronparse.dependency_export."""
import json

import pytest

from cronparse.dependency import DependencyGraph
from cronparse.dependency_export import from_json, to_json, to_text


def _make_graph() -> DependencyGraph:
    g = DependencyGraph()
    g.add("fetch", "0 * * * *", description="Fetch data")
    g.add("process", "30 * * * *", depends_on=["fetch"], description="Process data")
    g.add("report", "0 1 * * *", depends_on=["process"])
    return g


class TestDependencyExport:
    def test_to_json_returns_string(self):
        g = _make_graph()
        result = to_json(g)
        assert isinstance(result, str)

    def test_to_json_is_valid_json(self):
        g = _make_graph()
        parsed = json.loads(to_json(g))
        assert isinstance(parsed, list)

    def test_to_json_entry_count(self):
        g = _make_graph()
        parsed = json.loads(to_json(g))
        assert len(parsed) == 3

    def test_to_json_contains_required_keys(self):
        g = _make_graph()
        parsed = json.loads(to_json(g))
        for row in parsed:
            assert "name" in row
            assert "expression" in row
            assert "depends_on" in row
            assert "description" in row

    def test_to_json_preserves_depends_on(self):
        g = _make_graph()
        parsed = json.loads(to_json(g))
        process = next(r for r in parsed if r["name"] == "process")
        assert "fetch" in process["depends_on"]

    def test_from_json_round_trip(self):
        g = _make_graph()
        serialised = to_json(g)
        g2 = DependencyGraph()
        from_json(serialised, g2)
        assert len(g2.all()) == 3
        assert g2.get("fetch") is not None
        assert g2.get("process") is not None

    def test_from_json_restores_depends_on(self):
        g = _make_graph()
        serialised = to_json(g)
        g2 = DependencyGraph()
        from_json(serialised, g2)
        process = g2.get("process")
        assert process is not None
        assert "fetch" in process.depends_on

    def test_to_text_returns_string(self):
        g = _make_graph()
        result = to_text(g)
        assert isinstance(result, str)

    def test_to_text_contains_job_names(self):
        g = _make_graph()
        result = to_text(g)
        assert "fetch" in result
        assert "process" in result

    def test_to_text_empty_graph(self):
        g = DependencyGraph()
        result = to_text(g)
        assert "No jobs" in result
