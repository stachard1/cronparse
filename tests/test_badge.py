"""Tests for cronparse.badge."""
import pytest

from cronparse.badge import Badge, generate_badge


class TestGenerateBadge:
    def test_returns_badge_instance(self):
        badge = generate_badge("* * * * *")
        assert isinstance(badge, Badge)

    def test_valid_clean_expression_is_brightgreen(self):
        # hourly — no lint warnings expected
        badge = generate_badge("0 * * * *")
        assert badge.status == "valid"
        assert badge.color == "brightgreen"

    def test_invalid_expression_is_red(self):
        badge = generate_badge("99 * * * *")
        assert badge.status == "invalid"
        assert badge.color == "red"
        assert badge.message == "invalid"

    def test_every_minute_triggers_warning(self):
        # W002: runs every minute — lint should flag this
        badge = generate_badge("* * * * *")
        assert badge.status == "warning"
        assert badge.color == "yellow"

    def test_custom_label_is_used(self):
        badge = generate_badge("0 * * * *", label="backup")
        assert badge.label == "backup"

    def test_default_label_is_cron(self):
        badge = generate_badge("0 * * * *")
        assert badge.label == "cron"

    def test_expression_stored_on_badge(self):
        expr = "0 12 * * 1"
        badge = generate_badge(expr)
        assert badge.expression == expr

    def test_message_contains_human_description_when_valid(self):
        badge = generate_badge("0 12 * * 1")
        assert badge.message != ""
        assert badge.message != "invalid"

    def test_str_representation(self):
        badge = generate_badge("0 * * * *")
        text = str(badge)
        assert "cron" in text
        assert badge.status in text

    def test_to_dict_contains_required_keys(self):
        badge = generate_badge("0 * * * *")
        d = badge.to_dict()
        for key in ("expression", "label", "status", "color", "message"):
            assert key in d

    def test_to_dict_values_match_badge_fields(self):
        badge = generate_badge("0 6 * * *", label="morning")
        d = badge.to_dict()
        assert d["expression"] == "0 6 * * *"
        assert d["label"] == "morning"
        assert d["status"] == badge.status
        assert d["color"] == badge.color

    def test_to_shields_url_contains_color(self):
        badge = generate_badge("0 * * * *")
        url = badge.to_shields_url()
        assert badge.color in url
        assert "shields.io" in url

    def test_to_shields_url_custom_style(self):
        badge = generate_badge("0 * * * *")
        url = badge.to_shields_url(style="for-the-badge")
        assert "for-the-badge" in url
