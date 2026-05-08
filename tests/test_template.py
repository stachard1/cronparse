"""Tests for cronparse.template."""
import pytest

from cronparse.template import Template, TemplateRegistry


class TestTemplateRegistry:
    def _make(self) -> TemplateRegistry:
        return TemplateRegistry()

    # --- basic retrieval ---

    def test_get_builtin_by_name(self):
        reg = self._make()
        t = reg.get("hourly")
        assert t is not None
        assert t.expression == "0 * * * *"

    def test_get_unknown_returns_none(self):
        reg = self._make()
        assert reg.get("nonexistent") is None

    def test_all_returns_list_of_templates(self):
        reg = self._make()
        result = reg.all()
        assert isinstance(result, list)
        assert all(isinstance(t, Template) for t in result)

    def test_all_contains_builtins(self):
        reg = self._make()
        names = {t.name for t in reg.all()}
        assert "every_minute" in names
        assert "monthly_first" in names

    # --- register ---

    def test_register_adds_new_template(self):
        reg = self._make()
        custom = Template("custom", "0 3 * * *", "Daily at 3am", ["daily"])
        reg.register(custom)
        assert reg.get("custom") is custom

    def test_register_overwrites_existing(self):
        reg = self._make()
        updated = Template("hourly", "0 */2 * * *", "Every 2 hours")
        reg.register(updated)
        assert reg.get("hourly").expression == "0 */2 * * *"

    def test_register_empty_name_raises(self):
        reg = self._make()
        with pytest.raises(ValueError):
            reg.register(Template("", "* * * * *", "bad"))

    # --- by_tag ---

    def test_by_tag_returns_matching_templates(self):
        reg = self._make()
        daily = reg.by_tag("daily")
        assert all("daily" in [x.lower() for x in t.tags] for t in daily)
        assert len(daily) >= 1

    def test_by_tag_case_insensitive(self):
        reg = self._make()
        assert reg.by_tag("DAILY") == reg.by_tag("daily")

    def test_by_tag_unknown_returns_empty(self):
        reg = self._make()
        assert reg.by_tag("nonexistent_tag") == []

    # --- search ---

    def test_search_by_name_substring(self):
        reg = self._make()
        results = reg.search("hourly")
        names = {t.name for t in results}
        assert "hourly" in names

    def test_search_by_description_substring(self):
        reg = self._make()
        results = reg.search("midnight")
        assert any("midnight" in t.description.lower() for t in results)

    def test_search_case_insensitive(self):
        reg = self._make()
        assert reg.search("HOURLY") == reg.search("hourly")

    def test_search_no_match_returns_empty(self):
        reg = self._make()
        assert reg.search("zzznomatch") == []

    # --- remove ---

    def test_remove_existing_returns_true(self):
        reg = self._make()
        assert reg.remove("hourly") is True
        assert reg.get("hourly") is None

    def test_remove_nonexistent_returns_false(self):
        reg = self._make()
        assert reg.remove("ghost") is False

    # --- __str__ ---

    def test_template_str(self):
        t = Template("hourly", "0 * * * *", "Every hour at minute 0")
        assert "hourly" in str(t)
        assert "0 * * * *" in str(t)
        assert "Every hour" in str(t)
