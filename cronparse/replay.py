"""Replay cron execution history over a time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronparse.next_run import next_run
from cronparse.parser import CronExpression
from cronparse.validator import validate


@dataclass
class ReplayEntry:
    expression: str
    label: Optional[str]
    fired_at: datetime

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        ts = self.fired_at.strftime("%Y-%m-%d %H:%M")
        return f"[{ts}] {self.expression}{label_part}"


@dataclass
class ReplayResult:
    expression: str
    label: Optional[str]
    start: datetime
    end: datetime
    entries: List[ReplayEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"{self.expression}{label_part}: "
            f"{self.count} execution(s) between "
            f"{self.start.strftime('%Y-%m-%d %H:%M')} and "
            f"{self.end.strftime('%Y-%m-%d %H:%M')}"
        )


def replay(
    expression: str,
    start: datetime,
    end: datetime,
    label: Optional[str] = None,
    max_entries: int = 1000,
) -> ReplayResult:
    """Return all scheduled fire times for *expression* in [start, end]."""
    result = ReplayResult(expression=expression, label=label, start=start, end=end)

    validation = validate(expression)
    if not validation.valid:
        return result

    expr = CronExpression.parse(expression)
    current = start
    while current <= end and len(result.entries) < max_entries:
        runs = next_run(expr, from_dt=current, count=1)
        if not runs:
            break
        fired = runs[0]
        if fired > end:
            break
        result.entries.append(
            ReplayEntry(expression=expression, label=label, fired_at=fired)
        )
        # advance by one minute to avoid re-matching the same minute
        from datetime import timedelta
        current = fired + timedelta(minutes=1)

    return result
