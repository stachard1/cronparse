"""Watchlist: track cron expressions that should be monitored for changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.validator import validate


@dataclass
class WatchEntry:
    expression: str
    label: str
    added_at: datetime = field(default_factory=datetime.utcnow)
    last_changed: Optional[datetime] = None

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return f"{self.expression}{label_part} — watched since {self.added_at.isoformat()}"


class Watchlist:
    """Maintains a set of watched cron expressions keyed by label."""

    def __init__(self) -> None:
        self._entries: Dict[str, WatchEntry] = {}

    def add(self, expression: str, label: str) -> WatchEntry:
        """Add an expression to the watchlist under *label*."""
        if not label or not label.strip():
            raise ValueError("label must be a non-empty string")
        label = label.strip()
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression: {result.error}")
        entry = WatchEntry(expression=expression, label=label)
        self._entries[label] = entry
        return entry

    def remove(self, label: str) -> bool:
        """Remove entry by label. Returns True if removed, False if not found."""
        return self._entries.pop(label.strip(), None) is not None

    def update(self, label: str, new_expression: str) -> WatchEntry:
        """Update the expression for an existing watched label."""
        label = label.strip()
        if label not in self._entries:
            raise KeyError(f"No watched entry with label '{label}'")
        result = validate(new_expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression: {result.error}")
        entry = self._entries[label]
        entry.expression = new_expression
        entry.last_changed = datetime.utcnow()
        return entry

    def get(self, label: str) -> Optional[WatchEntry]:
        return self._entries.get(label.strip())

    def all(self) -> List[WatchEntry]:
        return list(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)
