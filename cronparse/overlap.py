"""Detect scheduling overlaps between cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from cronparse.next_run import next_run
from cronparse.parser import CronExpression


@dataclass
class OverlapResult:
    """Result of an overlap check between two cron expressions."""

    expr_a: str
    expr_b: str
    overlapping_times: List[datetime] = field(default_factory=list)

    @property
    def has_overlaps(self) -> bool:
        return len(self.overlapping_times) > 0

    @property
    def count(self) -> int:
        return len(self.overlapping_times)

    def __str__(self) -> str:
        if not self.has_overlaps:
            return f"No overlaps found between '{self.expr_a}' and '{self.expr_b}'"
        times = ", ".join(dt.strftime("%Y-%m-%d %H:%M") for dt in self.overlapping_times[:5])
        suffix = f" (+{self.count - 5} more)" if self.count > 5 else ""
        return (
            f"{self.count} overlap(s) between '{self.expr_a}' and '{self.expr_b}': "
            f"{times}{suffix}"
        )


def find_overlaps(
    expr_a: str,
    expr_b: str,
    *,
    start: datetime | None = None,
    periods: int = 100,
) -> OverlapResult:
    """Find datetime overlaps between two cron expressions.

    Compares the next *periods* run times of each expression and returns
    any datetimes that appear in both schedules.

    Args:
        expr_a: First cron expression string.
        expr_b: Second cron expression string.
        start: Datetime to begin scanning from. Defaults to now.
        periods: Number of future runs to compare for each expression.

    Returns:
        An :class:`OverlapResult` with any shared run times.
    """
    if start is None:
        start = datetime.now().replace(second=0, microsecond=0)

    parsed_a = CronExpression.parse(expr_a)
    parsed_b = CronExpression.parse(expr_b)

    runs_a: List[datetime] = next_run(parsed_a, start=start, count=periods)
    runs_b: List[datetime] = next_run(parsed_b, start=start, count=periods)

    set_b = set(runs_b)
    shared = sorted(dt for dt in runs_a if dt in set_b)

    return OverlapResult(expr_a=expr_a, expr_b=expr_b, overlapping_times=shared)
