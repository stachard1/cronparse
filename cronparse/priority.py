"""Priority levels and ordering for cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional

from cronparse.exceptions import CronParseError
from cronparse.parser import CronExpression


class PriorityLevel(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

    def __str__(self) -> str:
        return self.name.capitalize()


@dataclass
class PriorityEntry:
    expression: str
    level: PriorityLevel
    label: str = ""

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return f"[{self.level}] {self.expression}{label_part}"


@dataclass
class PriorityQueue:
    _entries: List[PriorityEntry] = field(default_factory=list)

    def add(
        self,
        expression: str,
        level: PriorityLevel = PriorityLevel.NORMAL,
        label: str = "",
    ) -> PriorityEntry:
        try:
            CronExpression(expression)
        except Exception as exc:
            raise CronParseError(f"Invalid expression: {expression}") from exc
        entry = PriorityEntry(expression=expression, level=level, label=label.strip())
        self._entries.append(entry)
        return entry

    def remove(self, expression: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.expression != expression]
        return len(self._entries) < before

    def get(self, level: Optional[PriorityLevel] = None) -> List[PriorityEntry]:
        entries = list(self._entries)
        if level is not None:
            entries = [e for e in entries if e.level == level]
        return sorted(entries, key=lambda e: e.level, reverse=True)

    def highest(self) -> Optional[PriorityEntry]:
        if not self._entries:
            return None
        return max(self._entries, key=lambda e: e.level)

    def __len__(self) -> int:
        return len(self._entries)
