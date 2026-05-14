"""Tests for cronparse.throttle."""
import pytest

from cronparse.exceptions import CronParseError
from cronparse.throttle import ThrottleRule, ThrottleCheckResult, ThrottleStore


class TestThrottleStore:
    def _make(self) -> ThrottleStore:
        return ThrottleStore()

    def test_add_returns_throttle_rule(self):
        store = self._make()
        rule = store.add("* * * * *", max_runs=5, window_seconds=300)
        assert isinstance(rule, ThrottleRule)

    def test_add_stores_entry(self):
        store = self._make()
        store.add("0 * * * *", max_runs=1, window_seconds=3600)
        assert len(store.all()) == 1

    def test_add_with_label(self):
        store = self._make()
        rule = store.add("0 0 * * *", max_runs=1, window_seconds=86400, label="daily job")
        assert rule.label == "daily job"

    def test_add_strips_label_whitespace(self):
        store = self._make()
        rule = store.add("0 0 * * *", max_runs=1, window_seconds=86400, label="  daily  ")
        assert rule.label == "daily"

    def test_add_invalid_expression_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.add("bad expr", max_runs=1, window_seconds=60)

    def test_add_invalid_max_runs_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add("* * * * *", max_runs=0, window_seconds=60)

    def test_add_invalid_window_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add("* * * * *", max_runs=1, window_seconds=0)

    def test_get_returns_rule(self):
        store = self._make()
        store.add("5 * * * *", max_runs=3, window_seconds=120)
        rule = store.get("5 * * * *")
        assert rule is not None
        assert rule.max_runs == 3

    def test_get_missing_returns_none(self):
        store = self._make()
        assert store.get("* * * * *") is None

    def test_remove_existing(self):
        store = self._make()
        store.add("* * * * *", max_runs=2, window_seconds=60)
        removed = store.remove("* * * * *")
        assert removed is True
        assert len(store.all()) == 0

    def test_remove_missing_returns_false(self):
        store = self._make()
        assert store.remove("* * * * *") is False

    def test_check_allowed(self):
        store = self._make()
        store.add("* * * * *", max_runs=5, window_seconds=300)
        result = store.check("* * * * *", run_count=3)
        assert isinstance(result, ThrottleCheckResult)
        assert result.allowed is True

    def test_check_throttled(self):
        store = self._make()
        store.add("* * * * *", max_runs=5, window_seconds=300)
        result = store.check("* * * * *", run_count=6)
        assert result is not None
        assert result.allowed is False

    def test_check_at_limit_is_allowed(self):
        store = self._make()
        store.add("* * * * *", max_runs=5, window_seconds=300)
        result = store.check("* * * * *", run_count=5)
        assert result.allowed is True

    def test_check_missing_rule_returns_none(self):
        store = self._make()
        assert store.check("* * * * *", run_count=1) is None

    def test_str_rule(self):
        rule = ThrottleRule(
            expression="0 * * * *",
            max_runs=10,
            window_seconds=3600,
            label="hourly",
        )
        text = str(rule)
        assert "hourly" in text
        assert "10" in text

    def test_str_check_result_allowed(self):
        store = self._make()
        store.add("* * * * *", max_runs=5, window_seconds=60)
        result = store.check("* * * * *", run_count=2)
        assert "allowed" in str(result)

    def test_str_check_result_throttled(self):
        store = self._make()
        store.add("* * * * *", max_runs=5, window_seconds=60)
        result = store.check("* * * * *", run_count=10)
        assert "throttled" in str(result)
