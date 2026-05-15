"""Blackout window support: suppress cron runs during defined time ranges."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional

from cronparse.exceptions import CronParseError
from cronparse.parser import CronExpression


@dataclass
class BlackoutWindow:
    """A named time-of-day blackout window."""

    expression: str
    start: time
    end: time
    label: str = ""

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"{self.expression} blacked out "
            f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"
            f"{label_part}"
        )

    def covers(self, dt: datetime) -> bool:
        """Return True if *dt* falls within this blackout window."""
        t = dt.time().replace(second=0, microsecond=0)
        if self.start <= self.end:
            return self.start <= t <= self.end
        # Overnight window e.g. 22:00 – 06:00
        return t >= self.start or t <= self.end


@dataclass
class BlackoutStore:
    """Registry of blackout windows keyed by cron expression."""

    _windows: List[BlackoutWindow] = field(default_factory=list)

    def add(
        self,
        expression: str,
        start: time,
        end: time,
        label: str = "",
    ) -> BlackoutWindow:
        """Register a blackout window for *expression*.

        Raises :class:`~cronparse.exceptions.CronParseError` if the
        expression is invalid.
        """
        try:
            CronExpression(expression)
        except Exception as exc:  # pragma: no cover – parser raises CronParseError
            raise CronParseError(str(exc)) from exc
        if start == end:
            raise ValueError("start and end times must differ")
        win = BlackoutWindow(expression=expression, start=start, end=end, label=label)
        self._windows.append(win)
        return win

    def remove(self, expression: str) -> int:
        """Remove all windows for *expression*. Returns count removed."""
        before = len(self._windows)
        self._windows = [w for w in self._windows if w.expression != expression]
        return before - len(self._windows)

    def windows_for(self, expression: str) -> List[BlackoutWindow]:
        """Return all blackout windows registered for *expression*."""
        return [w for w in self._windows if w.expression == expression]

    def is_blacked_out(self, expression: str, dt: datetime) -> bool:
        """Return True if *dt* falls inside any blackout window for *expression*."""
        return any(w.covers(dt) for w in self.windows_for(expression))

    def all(self) -> List[BlackoutWindow]:
        """Return a copy of all registered windows."""
        return list(self._windows)
