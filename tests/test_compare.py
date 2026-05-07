"""Tests for cronparse.compare."""

from __future__ import annotations

import pytest

from cronparse.compare import compare, CompareResult, FieldComparison


class TestCompare:
    def test_returns_compare_result_instance(self):
        result = compare("* * * * *", "* * * * *")
        assert isinstance(result, CompareResult)

    def test_identical_expressions_are_identical(self):
        result = compare("0 9 * * 1", "0 9 * * 1")
        assert result.identical is True

    def test_different_expressions_are_not_identical(self):
        result = compare("0 9 * * 1", "0 10 * * 1")
        assert result.identical is False

    def test_fields_populated_for_valid_expressions(self):
        result = compare("* * * * *", "0 * * * *")
        assert len(result.fields) == 5
        assert all(isinstance(f, FieldComparison) for f in result.fields)

    def test_differing_fields_returns_only_changed(self):
        result = compare("0 9 * * 1", "0 10 * * 1")
        diffs = result.differing_fields
        assert len(diffs) == 1
        assert diffs[0].field_name == "hour"

    def test_multiple_differing_fields(self):
        result = compare("0 9 1 * *", "30 18 * 6 1")
        assert len(result.differing_fields) == 4

    def test_invalid_left_expression(self):
        result = compare("not valid", "* * * * *")
        assert result.left_valid is False
        assert result.fields == []

    def test_invalid_right_expression(self):
        result = compare("* * * * *", "99 * * * *")
        assert result.right_valid is False
        assert result.fields == []

    def test_human_readable_set_for_valid_expressions(self):
        result = compare("* * * * *", "0 * * * *")
        assert result.left_human is not None
        assert result.right_human is not None

    def test_str_output_contains_field_names(self):
        result = compare("0 9 * * 1", "0 10 * * 1")
        output = str(result)
        assert "hour" in output

    def test_field_comparison_str(self):
        fc = FieldComparison(field_name="minute", left="0", right="*", match=False)
        s = str(fc)
        assert "minute" in s
        assert "≠" in s

    def test_field_comparison_match_str(self):
        fc = FieldComparison(field_name="hour", left="9", right="9", match=True)
        s = str(fc)
        assert "=" in s
