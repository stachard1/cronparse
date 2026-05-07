"""Compute similarity scores between cron expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .parser import CronExpression
from .next_run import next_run
from datetime import datetime


_FIELD_NAMES = ("minute", "hour", "day", "month", "weekday")
_SAMPLE_COUNT = 60  # number of next-run timestamps to compare


@dataclass
class SimilarityResult:
    expr_a: str
    expr_b: str
    field_score: float  # 0.0 – 1.0, fraction of identical fields
    schedule_score: float  # 0.0 – 1.0, overlap of sampled run-times
    overall_score: float  # weighted average

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"Similarity({self.expr_a!r} vs {self.expr_b!r}): "
            f"field={self.field_score:.2f}, "
            f"schedule={self.schedule_score:.2f}, "
            f"overall={self.overall_score:.2f}"
        )


def _field_similarity(a: CronExpression, b: CronExpression) -> float:
    """Return the fraction of fields whose resolved value sets are identical."""
    matches = 0
    for field in _FIELD_NAMES:
        set_a = set(getattr(a, field).values)
        set_b = set(getattr(b, field).values)
        if set_a == set_b:
            matches += 1
    return matches / len(_FIELD_NAMES)


def _schedule_similarity(
    expr_a: str, expr_b: str, anchor: datetime, count: int
) -> float:
    """Return the Jaccard similarity of the two next-run timestamp sets."""
    runs_a = set(next_run(expr_a, anchor, count))
    runs_b = set(next_run(expr_b, anchor, count))
    if not runs_a and not runs_b:
        return 1.0
    intersection = runs_a & runs_b
    union = runs_a | runs_b
    return len(intersection) / len(union) if union else 0.0


def compare(
    expr_a: str,
    expr_b: str,
    anchor: datetime | None = None,
    sample_count: int = _SAMPLE_COUNT,
    field_weight: float = 0.4,
) -> SimilarityResult:
    """Compare two cron expressions and return a :class:`SimilarityResult`.

    Parameters
    ----------
    expr_a, expr_b:
        Standard 5-field cron strings.
    anchor:
        Start datetime for next-run sampling (defaults to *now*).
    sample_count:
        How many future run-times to sample when computing schedule overlap.
    field_weight:
        Weight given to the field score (schedule weight = 1 - field_weight).
    """
    if anchor is None:
        anchor = datetime.now().replace(second=0, microsecond=0)

    parsed_a = CronExpression(expr_a)
    parsed_b = CronExpression(expr_b)

    fs = _field_similarity(parsed_a, parsed_b)
    ss = _schedule_similarity(expr_a, expr_b, anchor, sample_count)
    overall = field_weight * fs + (1 - field_weight) * ss

    return SimilarityResult(
        expr_a=expr_a,
        expr_b=expr_b,
        field_score=round(fs, 4),
        schedule_score=round(ss, 4),
        overall_score=round(overall, 4),
    )


def rank(
    target: str,
    candidates: List[str],
    anchor: datetime | None = None,
    sample_count: int = _SAMPLE_COUNT,
) -> List[Tuple[str, SimilarityResult]]:
    """Rank *candidates* by similarity to *target* (highest first)."""
    results = [
        (expr, compare(target, expr, anchor=anchor, sample_count=sample_count))
        for expr in candidates
    ]
    results.sort(key=lambda t: t[1].overall_score, reverse=True)
    return results
