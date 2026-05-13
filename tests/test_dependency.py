"""Tests for cronparse.dependency."""
import pytest

from cronparse.dependency import DependencyEntry, DependencyGraph
from cronparse.exceptions import CronParseError


class TestDependencyGraph:
    def _make(self) -> DependencyGraph:
        return DependencyGraph()

    def test_add_returns_dependency_entry(self):
        g = self._make()
        entry = g.add("job_a", "* * * * *")
        assert isinstance(entry, DependencyEntry)

    def test_add_stores_entry(self):
        g = self._make()
        g.add("job_a", "0 * * * *")
        assert g.get("job_a") is not None

    def test_add_invalid_expression_raises(self):
        g = self._make()
        with pytest.raises(CronParseError):
            g.add("job_a", "99 * * * *")

    def test_add_empty_name_raises(self):
        g = self._make()
        with pytest.raises(ValueError):
            g.add("", "* * * * *")

    def test_add_duplicate_name_raises(self):
        g = self._make()
        g.add("job_a", "* * * * *")
        with pytest.raises(ValueError):
            g.add("job_a", "0 * * * *")

    def test_add_with_depends_on(self):
        g = self._make()
        g.add("job_a", "* * * * *")
        entry = g.add("job_b", "0 * * * *", depends_on=["job_a"])
        assert "job_a" in entry.depends_on

    def test_remove_entry(self):
        g = self._make()
        g.add("job_a", "* * * * *")
        g.remove("job_a")
        assert g.get("job_a") is None

    def test_all_returns_all_entries(self):
        g = self._make()
        g.add("job_a", "* * * * *")
        g.add("job_b", "0 * * * *")
        assert len(g.all()) == 2

    def test_dependencies_of(self):
        g = self._make()
        g.add("job_a", "* * * * *")
        g.add("job_b", "0 * * * *", depends_on=["job_a"])
        deps = g.dependencies_of("job_b")
        assert len(deps) == 1
        assert deps[0].name == "job_a"

    def test_dependents_of(self):
        g = self._make()
        g.add("job_a", "* * * * *")
        g.add("job_b", "0 * * * *", depends_on=["job_a"])
        dependents = g.dependents_of("job_a")
        assert any(e.name == "job_b" for e in dependents)

    def test_no_cycle_simple_chain(self):
        g = self._make()
        g.add("a", "* * * * *")
        g.add("b", "0 * * * *", depends_on=["a"])
        g.add("c", "0 0 * * *", depends_on=["b"])
        assert not g.has_cycle()

    def test_cycle_detected(self):
        g = self._make()
        g.add("a", "* * * * *", depends_on=["c"])
        g.add("b", "0 * * * *", depends_on=["a"])
        g.add("c", "0 0 * * *", depends_on=["b"])
        assert g.has_cycle()

    def test_topological_order_simple(self):
        g = self._make()
        g.add("a", "* * * * *")
        g.add("b", "0 * * * *", depends_on=["a"])
        order = g.topological_order()
        assert order.index("a") < order.index("b")

    def test_topological_order_raises_on_cycle(self):
        g = self._make()
        g.add("a", "* * * * *", depends_on=["b"])
        g.add("b", "0 * * * *", depends_on=["a"])
        with pytest.raises(ValueError):
            g.topological_order()

    def test_str_representation(self):
        g = self._make()
        entry = g.add("job_a", "* * * * *")
        assert "job_a" in str(entry)
