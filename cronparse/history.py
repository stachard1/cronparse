"""Cron expression history and change tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronparse.parser import CronExpression
from cronparse.exceptions import CronParseError


@dataclass
class HistoryEntry:
    expression: str
    label: Optional[str]
    added_at: datetime

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return f"[{self.added_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.expression}{label_part}"


@dataclass
class CronHistory:
    entries: List[HistoryEntry] = field(default_factory=list)

    def add(self, expression: str, label: Optional[str] = None) -> HistoryEntry:
        """Add a cron expression to history, raises CronParseError if invalid."""
        CronExpression(expression)  # validate by parsing
        entry = HistoryEntry(
            expression=expression,
            label=label,
            added_at=datetime.utcnow(),
        )
        self.entries.append(entry)
        return entry

    def remove(self, expression: str) -> int:
        """Remove all entries matching expression. Returns count removed."""
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.expression != expression]
        return before - len(self.entries)

    def find(self, expression: str) -> List[HistoryEntry]:
        """Return all entries matching the given expression."""
        return [e for e in self.entries if e.expression == expression]

    def clear(self) -> None:
        """Remove all history entries."""
        self.entries.clear()

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)
