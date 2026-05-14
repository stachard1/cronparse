"""Quota enforcement: cap how many times a cron job may run in a time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronparse.exceptions import CronParseError
from cronparse.validator import validate


@dataclass
class QuotaEntry:
    expression: str
    max_runs: int
    window_hours: int
    label: str = ""

    def __str__(self) -> str:  # pragma: no cover
        lbl = f" ({self.label})" if self.label else ""
        return f"{self.expression}{lbl} — max {self.max_runs} runs per {self.window_hours}h"


@dataclass
class QuotaCheckResult:
    entry: QuotaEntry
    runs_in_window: int
    exceeded: bool

    def __str__(self) -> str:  # pragma: no cover
        status = "EXCEEDED" if self.exceeded else "OK"
        return (
            f"{self.entry.expression}: {self.runs_in_window}/{self.entry.max_runs} "
            f"in {self.entry.window_hours}h window [{status}]"
        )


@dataclass
class QuotaStore:
    _entries: List[QuotaEntry] = field(default_factory=list)

    def add(
        self,
        expression: str,
        max_runs: int,
        window_hours: int,
        label: str = "",
    ) -> QuotaEntry:
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression: {expression}")
        if max_runs < 1:
            raise ValueError("max_runs must be >= 1")
        if window_hours < 1:
            raise ValueError("window_hours must be >= 1")
        entry = QuotaEntry(
            expression=expression,
            max_runs=max_runs,
            window_hours=window_hours,
            label=label.strip(),
        )
        self._entries.append(entry)
        return entry

    def remove(self, expression: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.expression != expression]
        return len(self._entries) < before

    def get(self, expression: str) -> Optional[QuotaEntry]:
        for e in self._entries:
            if e.expression == expression:
                return e
        return None

    def all(self) -> List[QuotaEntry]:
        return list(self._entries)

    def check(
        self, entry: QuotaEntry, run_times: List[datetime]
    ) -> QuotaCheckResult:
        """Count how many *run_times* fall within the most recent window."""
        if not run_times:
            return QuotaCheckResult(entry=entry, runs_in_window=0, exceeded=False)
        window_start = max(run_times) - timedelta(hours=entry.window_hours)
        count = sum(1 for t in run_times if t >= window_start)
        return QuotaCheckResult(
            entry=entry,
            runs_in_window=count,
            exceeded=count > entry.max_runs,
        )
