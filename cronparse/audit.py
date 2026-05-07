"""Audit log for cron expression changes tracked over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AuditEvent:
    """A single recorded change event for a cron expression."""

    expression: str
    action: str  # 'added' | 'removed' | 'updated' | 'validated'
    label: Optional[str] = None
    note: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        label_part = f" [{self.label}]" if self.label else ""
        note_part = f" — {self.note}" if self.note else ""
        return f"{ts} | {self.action.upper():10s} | {self.expression}{label_part}{note_part}"


@dataclass
class AuditLog:
    """Ordered collection of AuditEvents."""

    _events: List[AuditEvent] = field(default_factory=list)

    def record(
        self,
        expression: str,
        action: str,
        label: Optional[str] = None,
        note: Optional[str] = None,
    ) -> AuditEvent:
        """Append a new event and return it."""
        event = AuditEvent(expression=expression, action=action, label=label, note=note)
        self._events.append(event)
        return event

    def events(self) -> List[AuditEvent]:
        """Return all recorded events in insertion order."""
        return list(self._events)

    def filter_by_action(self, action: str) -> List[AuditEvent]:
        """Return events matching *action* (case-insensitive)."""
        action_lower = action.lower()
        return [e for e in self._events if e.action.lower() == action_lower]

    def filter_by_expression(self, expression: str) -> List[AuditEvent]:
        """Return events whose expression matches exactly."""
        return [e for e in self._events if e.expression == expression]

    def clear(self) -> None:
        """Remove all events from the log."""
        self._events.clear()

    def __len__(self) -> int:
        return len(self._events)
