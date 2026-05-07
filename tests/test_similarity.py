"""Tests for cronparse.similarity."""

from datetime import datetime

import pytest

from cronparse.similarity import SimilarityResult, compare, rank


_ANCHOR = datetime(2024, 1, 1, 0, 0, 0)


class TestCompare:
    def test_returns_similarity_result(self):
        result = compare("* * * * *", "* * * * *", anchor=_ANCHOR)
        assert isinstance(result, SimilarityResult)

    def test_identical_expressions_score_one(self):
        result = compare("0 9 * * 1", "0 9 * * 1", anchor=_ANCHOR)
        assert result.field_score == 1.0
        assert result.schedule_score == 1.0
        assert result.overall_score == 1.0

    def test_completely_different_expressions_low_score(self):
        # Every minute vs. once a year — very little overlap.
        result = compare("* * * * *", "0 0 1 1 *", anchor=_ANCHOR, sample_count=60)
        assert result.overall_score < 0.5

    def test_field_score_partial_match(self):
        # Same minute & hour, different day/month/weekday.
        result = compare("30 6 * * *", "30 6 1 1 1", anchor=_ANCHOR)
        # minute and hour match → 2/5 = 0.4
        assert result.field_score == pytest.approx(0.4)

    def test_schedule_score_between_zero_and_one(self):
        result = compare("0 * * * *", "30 * * * *", anchor=_ANCHOR, sample_count=24)
        assert 0.0 <= result.schedule_score <= 1.0

    def test_expr_a_and_expr_b_stored(self):
        result = compare("5 4 * * *", "10 3 * * *", anchor=_ANCHOR)
        assert result.expr_a == "5 4 * * *"
        assert result.expr_b == "10 3 * * *"

    def test_overall_is_weighted_average(self):
        result = compare(
            "0 9 * * 1", "0 9 * * 1", anchor=_ANCHOR, field_weight=0.4
        )
        expected = 0.4 * result.field_score + 0.6 * result.schedule_score
        assert result.overall_score == pytest.approx(expected, abs=1e-4)

    def test_custom_field_weight(self):
        result_low = compare("0 9 * * *", "0 9 1 * *", anchor=_ANCHOR, field_weight=0.1)
        result_high = compare("0 9 * * *", "0 9 1 * *", anchor=_ANCHOR, field_weight=0.9)
        # With higher field_weight the field_score dominates more;
        # the two results should differ.
        assert result_low.overall_score != result_high.overall_score

    def test_anchor_defaults_to_now(self):
        # Should not raise when anchor is omitted.
        result = compare("* * * * *", "* * * * *")
        assert result.overall_score == 1.0


class TestRank:
    def test_returns_list_of_tuples(self):
        candidates = ["0 9 * * *", "30 6 * * *", "0 9 * * *"]
        results = rank("0 9 * * *", candidates, anchor=_ANCHOR)
        assert isinstance(results, list)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

    def test_identical_candidate_ranked_first(self):
        candidates = ["30 6 * * *", "0 9 * * *", "0 0 1 1 *"]
        results = rank("0 9 * * *", candidates, anchor=_ANCHOR)
        top_expr, top_result = results[0]
        assert top_expr == "0 9 * * *"
        assert top_result.overall_score == 1.0

    def test_results_sorted_descending(self):
        candidates = ["0 0 1 1 *", "* * * * *", "0 9 * * *"]
        results = rank("0 9 * * *", candidates, anchor=_ANCHOR)
        scores = [r.overall_score for _, r in results]
        assert scores == sorted(scores, reverse=True)

    def test_empty_candidates_returns_empty(self):
        results = rank("0 9 * * *", [], anchor=_ANCHOR)
        assert results == []
