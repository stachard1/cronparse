"""Statistics and frequency analysis for cron history entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from cronparse.history import CronHistory
from cronparse.next_run import next_run

from datetime import datetime, timedelta


@dataclass
class CronStats:
    expression: str
    label: str
    runs_per_hour: float
    runs_per_day: float
    runs_per_week: float
    next_5_runs: List[datetime]

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Label      : {self.label or '(none)'}",
            f"Runs/hour  : {self.runs_per_hour:.2f}",
            f"Runs/day   : {self.runs_per_day:.2f}",
            f"Runs/week  : {self.runs_per_week:.2f}",
            "Next 5 runs:",
        ]
        for dt in self.next_5_runs:
            lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)


def _count_runs_in_window(expression: str, start: datetime, hours: int) -> int:
    """Count how many times a cron expression fires within *hours* from *start*."""
    end = start + timedelta(hours=hours)
    runs = next_run(expression, start, count=hours * 60)  # upper bound
    return sum(1 for dt in runs if dt < end)


def compute_stats(expression: str, label: str = "", reference: datetime | None = None) -> CronStats:
    """Return frequency statistics for a single cron expression."""
    ref = reference or datetime.now().replace(second=0, microsecond=0)

    runs_per_hour = _count_runs_in_window(expression, ref, 1)
    runs_per_day = _count_runs_in_window(expression, ref, 24)
    runs_per_week = _count_runs_in_window(expression, ref, 168)

    next_5 = next_run(expression, ref, count=5)

    return CronStats(
        expression=expression,
        label=label,
        runs_per_hour=float(runs_per_hour),
        runs_per_day=float(runs_per_day),
        runs_per_week=float(runs_per_week),
        next_5_runs=next_5,
    )


def history_stats(history: CronHistory, reference: datetime | None = None) -> List[CronStats]:
    """Return stats for every entry in a CronHistory."""
    return [
        compute_stats(entry.expression, label=entry.label or "", reference=reference)
        for entry in history.entries
    ]
