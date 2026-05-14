"""Cooldown enforcement: prevent a cron job from running more frequently than allowed."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.validator import validate


@dataclass
class CooldownEntry:
    expression: str
    min_interval_seconds: int
    label: str = ""

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"CooldownEntry[{self.expression}{label_part}, "
            f"min_interval={self.min_interval_seconds}s]"
        )

    @property
    def min_interval(self) -> timedelta:
        return timedelta(seconds=self.min_interval_seconds)


@dataclass
class CooldownStore:
    _entries: Dict[str, CooldownEntry] = field(default_factory=dict)

    def add(
        self,
        expression: str,
        min_interval_seconds: int,
        label: str = "",
    ) -> CooldownEntry:
        """Register a cooldown rule for *expression*.

        Raises CronParseError if the expression is invalid or
        min_interval_seconds is not a positive integer.
        """
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression: {result.error}")
        if min_interval_seconds <= 0:
            raise ValueError("min_interval_seconds must be a positive integer")
        entry = CooldownEntry(
            expression=expression,
            min_interval_seconds=min_interval_seconds,
            label=label.strip(),
        )
        self._entries[expression] = entry
        return entry

    def remove(self, expression: str) -> bool:
        """Remove the cooldown rule for *expression*. Returns True if removed."""
        if expression in self._entries:
            del self._entries[expression]
            return True
        return False

    def get(self, expression: str) -> Optional[CooldownEntry]:
        """Return the CooldownEntry for *expression*, or None."""
        return self._entries.get(expression)

    def all(self) -> List[CooldownEntry]:
        """Return all registered cooldown entries."""
        return list(self._entries.values())

    def is_allowed(
        self,
        expression: str,
        seconds_since_last_run: Optional[float],
    ) -> bool:
        """Return True if the job may run given the elapsed time since last run.

        If no cooldown is registered for *expression*, always returns True.
        If *seconds_since_last_run* is None (never run), always returns True.
        """
        entry = self._entries.get(expression)
        if entry is None:
            return True
        if seconds_since_last_run is None:
            return True
        return seconds_since_last_run >= entry.min_interval_seconds
