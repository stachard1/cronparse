"""Annotation support for cron expressions — attach notes to history entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError


@dataclass
class Annotation:
    expression: str
    note: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        ts = self.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"[{ts}] {self.expression!r}: {self.note}"


class AnnotationStore:
    """Stores zero or more text annotations keyed by cron expression string."""

    def __init__(self) -> None:
        self._data: Dict[str, List[Annotation]] = {}

    def add(self, expression: str, note: str) -> Annotation:
        """Add a note for *expression*. Raises CronParseError if note is blank."""
        if not note or not note.strip():
            raise CronParseError("Annotation note must not be empty.")
        annotation = Annotation(expression=expression, note=note.strip())
        self._data.setdefault(expression, []).append(annotation)
        return annotation

    def get(self, expression: str) -> List[Annotation]:
        """Return all annotations for *expression* (newest-last order)."""
        return list(self._data.get(expression, []))

    def remove(self, expression: str, index: int) -> Annotation:
        """Remove annotation at *index* for *expression*. Raises IndexError if missing."""
        annotations = self._data.get(expression, [])
        if not annotations:
            raise IndexError(f"No annotations found for expression {expression!r}.")
        removed = annotations.pop(index)
        if not annotations:
            del self._data[expression]
        return removed

    def all_expressions(self) -> List[str]:
        """Return list of expressions that have at least one annotation."""
        return list(self._data.keys())

    def clear(self, expression: str) -> int:
        """Remove all annotations for *expression*. Returns count removed."""
        removed = self._data.pop(expression, [])
        return len(removed)

    def total(self) -> int:
        """Return total number of annotations across all expressions."""
        return sum(len(v) for v in self._data.values())
