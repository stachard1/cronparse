"""Ceiling module: find the latest possible run time within a window.

Provides CeilingResult and compute_ceiling, which determine the last
scheduled execution of a cron expression before a given deadline.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from .parser import CronExpression
from .next_run import next_run
from .validator import validate
from .exceptions import CronParseError


@dataclass
class CeilingResult:
    """Result of a ceiling computation.

    Attributes:
        expression: The cron expression that was evaluated.
        deadline: The upper bound datetime supplied by the caller.
        last_run: The latest scheduled run at or before *deadline*, or
            ``None`` when no run falls inside the search window.
        window_start: The start of the search window.
        window_end: The end of the search window (i.e. *deadline*).
        found: Whether a matching run was found.
    """

    expression: str
    deadline: datetime
    last_run: Optional[datetime]
    window_start: datetime
    window_end: datetime
    found: bool

    def __str__(self) -> str:  # noqa: D105
        if not self.found:
            return (
                f"No runs of '{self.expression}' found before "
                f"{self.deadline.strftime('%Y-%m-%d %H:%M')}"
            )
        assert self.last_run is not None
        return (
            f"Last run of '{self.expression}' before "
            f"{self.deadline.strftime('%Y-%m-%d %H:%M')}: "
            f"{self.last_run.strftime('%Y-%m-%d %H:%M')}"
        )


def compute_ceiling(
    expression: str,
    deadline: datetime,
    *,
    window_hours: int = 24 * 7,
    max_iterations: int = 10_000,
) -> CeilingResult:
    """Return the last scheduled run of *expression* at or before *deadline*.

    The function walks forward from ``deadline - window_hours`` in one-minute
    steps (via :func:`~cronparse.next_run.next_run`) and records every
    matching timestamp, returning the latest one that does not exceed
    *deadline*.

    Args:
        expression: A 5-field cron expression string.
        deadline: The upper bound; runs strictly after this moment are ignored.
        window_hours: How many hours before *deadline* to start searching.
            Defaults to 168 (one week).
        max_iterations: Safety cap on the number of ``next_run`` calls to
            prevent infinite loops on exotic expressions.

    Returns:
        A :class:`CeilingResult` describing the outcome.

    Raises:
        CronParseError: If *expression* is invalid.
    """
    result = validate(expression)
    if not result.valid:
        raise CronParseError(f"Invalid cron expression: {result.errors}")

    expr = CronExpression(expression)

    # Truncate to minute precision so comparisons are clean.
    deadline = deadline.replace(second=0, microsecond=0)
    window_start = deadline - timedelta(hours=window_hours)

    last_run: Optional[datetime] = None
    current = window_start
    iterations = 0

    while iterations < max_iterations:
        runs = next_run(expr, from_dt=current, count=1)
        if not runs:
            break
        candidate = runs[0].replace(second=0, microsecond=0)
        if candidate > deadline:
            break
        last_run = candidate
        # Advance one minute past the candidate to find the next occurrence.
        current = candidate + timedelta(minutes=1)
        iterations += 1

    return CeilingResult(
        expression=expression,
        deadline=deadline,
        last_run=last_run,
        window_start=window_start,
        window_end=deadline,
        found=last_run is not None,
    )
