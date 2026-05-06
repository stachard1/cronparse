"""Tests for cronparse.search."""

import pytest

from cronparse.history import CronHistory
from cronparse.search import SearchQuery, search
from cronparse.tags import TagIndex


EXPR_A = "* * * * *"
EXPR_B = "0 9 * * 1"
EXPR_C = "30 18 * * 5"


def _make_history() -> CronHistory:
    h = CronHistory()
    h.add(EXPR_A, label="every minute")
    h.add(EXPR_B, label="Monday morning")
    h.add(EXPR_C, label="Friday evening")
    return h


class TestSearch:
    def test_empty_query_returns_all(self):
        h = _make_history()
        results = search(h, SearchQuery())
        assert len(results) == 3

    def test_filter_by_label_substring(self):
        h = _make_history()
        results = search(h, SearchQuery(label="morning"))
        assert len(results) == 1
        assert results[0].expression == EXPR_B

    def test_filter_by_label_case_insensitive(self):
        h = _make_history()
        results = search(h, SearchQuery(label="FRIDAY"))
        assert len(results) == 1
        assert results[0].expression == EXPR_C

    def test_filter_by_expression_contains(self):
        h = _make_history()
        results = search(h, SearchQuery(expression_contains="0 9"))
        assert len(results) == 1
        assert results[0].expression == EXPR_B

    def test_filter_by_tag(self):
        h = _make_history()
        idx = TagIndex()
        idx.add(EXPR_A, "frequent")
        idx.add(EXPR_B, "weekly")
        results = search(h, SearchQuery(tag="weekly"), tag_index=idx)
        assert len(results) == 1
        assert results[0].expression == EXPR_B

    def test_combined_label_and_expression_filter(self):
        h = _make_history()
        results = search(h, SearchQuery(label="day", expression_contains="* 1"))
        assert len(results) == 1
        assert results[0].expression == EXPR_B

    def test_no_match_returns_empty_list(self):
        h = _make_history()
        results = search(h, SearchQuery(label="nonexistent"))
        assert results == []

    def test_tag_filter_without_index_raises(self):
        h = _make_history()
        with pytest.raises(ValueError, match="tag_index"):
            search(h, SearchQuery(tag="weekly"))

    def test_entry_without_label_skipped_when_label_filter_set(self):
        h = CronHistory()
        h.add(EXPR_A)  # no label
        h.add(EXPR_B, label="Monday morning")
        results = search(h, SearchQuery(label="Monday"))
        assert len(results) == 1
        assert results[0].expression == EXPR_B
