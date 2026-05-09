"""Reminder module: attach due-date reminders to cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronparse.exceptions import CronParseError
from cronparse.validator import validate


@dataclass
class Reminder:
    expression: str
    message: str
    due: datetime
    label: Optional[str] = None

    def __str__(self) -> str:
        label_part = f" [{self.label}]" if self.label else ""
        return f"{self.expression}{label_part} — {self.message} (due {self.due.isoformat()})"

    def is_overdue(self, now: Optional[datetime] = None) -> bool:
        """Return True if the due datetime has passed."""
        now = now or datetime.utcnow()
        return now >= self.due


@dataclass
class ReminderStore:
    _reminders: List[Reminder] = field(default_factory=list)

    def add(
        self,
        expression: str,
        message: str,
        due: datetime,
        label: Optional[str] = None,
    ) -> Reminder:
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression: {result.error}")
        message = message.strip()
        if not message:
            raise ValueError("message must not be empty")
        reminder = Reminder(
            expression=expression,
            message=message,
            due=due,
            label=label.strip() if label else None,
        )
        self._reminders.append(reminder)
        return reminder

    def remove(self, reminder: Reminder) -> bool:
        try:
            self._reminders.remove(reminder)
            return True
        except ValueError:
            return False

    def all(self) -> List[Reminder]:
        return list(self._reminders)

    def overdue(self, now: Optional[datetime] = None) -> List[Reminder]:
        """Return all reminders whose due date has passed."""
        return [r for r in self._reminders if r.is_overdue(now)]

    def for_expression(self, expression: str) -> List[Reminder]:
        """Return all reminders attached to a specific cron expression."""
        return [r for r in self._reminders if r.expression == expression]

    def __len__(self) -> int:
        return len(self._reminders)
