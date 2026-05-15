"""Forecast module: project cron run counts over a future time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from .next_run import next_run
from .validator import validate
from .exceptions import CronParseError


@dataclass
class ForecastWindow:
    """Result of a forecast computation for a single expression."""

    expression: str
    start: datetime
    end: datetime
    run_times: List[datetime] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.run_times)

    @property
    def duration_hours(self) -> float:
        delta = self.end - self.start
        return delta.total_seconds() / 3600

    @property
    def runs_per_hour(self) -> float:
        if self.duration_hours == 0:
            return 0.0
        return self.count / self.duration_hours

    def __str__(self) -> str:
        return (
            f"ForecastWindow({self.expression!r}, "
            f"runs={self.count}, "
            f"window={self.duration_hours:.1f}h, "
            f"rate={self.runs_per_hour:.2f}/h)"
        )


def forecast(
    expression: str,
    start: datetime,
    hours: int = 24,
    *,
    max_runs: int = 10_000,
) -> ForecastWindow:
    """Return all scheduled run times for *expression* in the window
    [start, start + hours).

    Args:
        expression: A valid 5-field cron expression.
        start:      Window start (inclusive).
        hours:      Window length in hours (default 24).
        max_runs:   Safety cap to prevent infinite loops.

    Returns:
        A :class:`ForecastWindow` instance.

    Raises:
        CronParseError: If *expression* is invalid.
    """
    result = validate(expression)
    if not result.valid:
        raise CronParseError(str(result))

    end = start + timedelta(hours=hours)
    runs: List[datetime] = []
    cursor = start

    while len(runs) < max_runs:
        candidates = next_run(expression, n=1, after=cursor)
        if not candidates:
            break
        nxt = candidates[0]
        if nxt >= end:
            break
        runs.append(nxt)
        cursor = nxt + timedelta(minutes=1)

    return ForecastWindow(
        expression=expression,
        start=start,
        end=end,
        run_times=runs,
    )
