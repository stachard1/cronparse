"""Tests for cronparse.suggest."""

import pytest

from cronparse.suggest import Suggestion, suggest


class TestSuggest:
    def test_returns_list_of_suggestion_instances(self):
        results = suggest("every minute")
        assert isinstance(results, list)
        assert all(isinstance(r, Suggestion) for r in results)

    def test_empty_query_returns_up_to_max_results(self):
        results = suggest("", max_results=3)
        assert len(results) == 3

    def test_empty_query_default_max(self):
        results = suggest("")
        assert len(results) == 5

    def test_exact_phrase_match(self):
        results = suggest("every minute")
        assert any(r.expression == "* * * * *" for r in results)

    def test_partial_word_match(self):
        results = suggest("midnight", max_results=10)
        assert all("midnight" in r.description for r in results)

    def test_multi_word_query_all_words_required(self):
        results = suggest("weekday midnight", max_results=10)
        for r in results:
            assert "weekday" in r.description.lower()
            assert "midnight" in r.description.lower()

    def test_no_match_returns_empty_list(self):
        results = suggest("xyzzy frobnicator")
        assert results == []

    def test_case_insensitive_query(self):
        lower = suggest("every hour")
        upper = suggest("EVERY HOUR")
        assert [r.expression for r in lower] == [r.expression for r in upper]

    def test_max_results_respected(self):
        results = suggest("", max_results=2)
        assert len(results) == 2

    def test_max_results_zero_raises(self):
        with pytest.raises(ValueError):
            suggest("", max_results=0)

    def test_suggestion_str_contains_expression_and_description(self):
        s = Suggestion("0 * * * *", "every hour")
        text = str(s)
        assert "0 * * * *" in text
        assert "every hour" in text

    def test_hourly_suggestion_present(self):
        results = suggest("every hour, on the hour")
        assert any(r.expression == "0 * * * *" for r in results)

    def test_weekday_suggestion_present(self):
        results = suggest("weekdays", max_results=10)
        expressions = [r.expression for r in results]
        assert "0 9-17 * * 1-5" in expressions or "0 0 * * 1-5" in expressions
