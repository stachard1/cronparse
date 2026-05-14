"""Tests for cronparse.notification."""
import pytest

from cronparse.notification import NotificationRule, NotificationStore
from cronparse.exceptions import CronParseError


class TestNotificationStore:
    def _make(self) -> NotificationStore:
        return NotificationStore()

    def test_add_returns_notification_rule(self):
        store = self._make()
        rule = store.add("* * * * *", "email")
        assert isinstance(rule, NotificationRule)

    def test_add_stores_rule(self):
        store = self._make()
        store.add("0 9 * * *", "slack")
        assert len(store.all()) == 1

    def test_add_with_label(self):
        store = self._make()
        rule = store.add("0 9 * * *", "slack", label="morning")
        assert rule.label == "morning"

    def test_add_strips_label_whitespace(self):
        store = self._make()
        rule = store.add("0 9 * * *", "slack", label="  daily  ")
        assert rule.label == "daily"

    def test_add_invalid_expression_raises(self):
        store = self._make()
        with pytest.raises(CronParseError):
            store.add("invalid", "email")

    def test_add_empty_channel_raises(self):
        store = self._make()
        with pytest.raises(ValueError):
            store.add("* * * * *", "   ")

    def test_rule_enabled_by_default(self):
        store = self._make()
        rule = store.add("* * * * *", "webhook")
        assert rule.enabled is True

    def test_add_disabled_rule(self):
        store = self._make()
        rule = store.add("* * * * *", "webhook", enabled=False)
        assert rule.enabled is False

    def test_disable_rule(self):
        store = self._make()
        store.add("0 * * * *", "email")
        result = store.disable("0 * * * *")
        assert result is True
        assert store.all()[0].enabled is False

    def test_enable_rule(self):
        store = self._make()
        store.add("0 * * * *", "email", enabled=False)
        store.enable("0 * * * *")
        assert store.all()[0].enabled is True

    def test_disable_unknown_returns_false(self):
        store = self._make()
        assert store.disable("0 0 * * *") is False

    def test_active_filters_disabled(self):
        store = self._make()
        store.add("* * * * *", "a")
        store.add("0 9 * * *", "b", enabled=False)
        assert len(store.active()) == 1

    def test_remove_existing(self):
        store = self._make()
        store.add("0 0 * * *", "email")
        removed = store.remove("0 0 * * *")
        assert removed is True
        assert len(store.all()) == 0

    def test_remove_nonexistent_returns_false(self):
        store = self._make()
        assert store.remove("0 0 * * *") is False

    def test_by_channel(self):
        store = self._make()
        store.add("* * * * *", "slack")
        store.add("0 9 * * *", "email")
        store.add("0 0 * * 1", "slack")
        slack_rules = store.by_channel("slack")
        assert len(slack_rules) == 2

    def test_str_representation(self):
        store = self._make()
        rule = store.add("* * * * *", "email", label="test")
        assert "email" in str(rule)
        assert "test" in str(rule)
