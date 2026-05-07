"""Tests for cronparse.lint."""
import pytest

from cronparse.lint import lint, LintResult, LintWarning


class TestLint:
    def test_returns_lint_result_instance(self):
        result = lint("* * * * *")
        assert isinstance(result, LintResult)

    def test_clean_expression_has_no_warnings(self):
        result = lint("0 9 * * 1")
        assert result.clean is True
        assert result.warnings == []

    def test_invalid_expression_returns_empty_warnings(self):
        # Validation errors take precedence; lint warnings list is empty.
        result = lint("99 * * * *")
        assert result.warnings == []

    def test_every_minute_triggers_w002(self):
        result = lint("* * * * *")
        codes = [w.code for w in result.warnings]
        assert "W002" in codes

    def test_every_minute_not_clean(self):
        result = lint("* * * * *")
        assert result.clean is False

    def test_feb_29_triggers_w001(self):
        result = lint("0 0 29 2 *")
        codes = [w.code for w in result.warnings]
        assert "W001" in codes

    def test_feb_29_warning_field(self):
        result = lint("0 0 29 2 *")
        w001 = next(w for w in result.warnings if w.code == "W001")
        assert w001.field == "day_of_month"

    def test_dom_and_dow_both_set_triggers_w003(self):
        result = lint("0 12 15 * 1")
        codes = [w.code for w in result.warnings]
        assert "W003" in codes

    def test_wildcard_dom_with_dow_no_w003(self):
        result = lint("0 9 * * 1")
        codes = [w.code for w in result.warnings]
        assert "W003" not in codes

    def test_wildcard_dow_with_dom_no_w003(self):
        result = lint("0 0 1 * *")
        codes = [w.code for w in result.warnings]
        assert "W003" not in codes

    def test_str_clean(self):
        result = lint("0 6 * * *")
        assert "OK" in str(result)

    def test_str_with_warnings(self):
        result = lint("* * * * *")
        text = str(result)
        assert "warning" in text
        assert "W002" in text

    def test_lint_warning_str(self):
        w = LintWarning(field="minute", code="W002", message="Too frequent.")
        assert "W002" in str(w)
        assert "minute" in str(w)

    def test_multiple_warnings_accumulated(self):
        # day 29 of Feb AND both dom+dow set
        result = lint("0 0 29 2 1")
        codes = [w.code for w in result.warnings]
        assert "W001" in codes
        assert "W003" in codes
