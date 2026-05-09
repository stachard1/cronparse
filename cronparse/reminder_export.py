"""Serialisation helpers for ReminderStore."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from cronparse.reminder import Reminder, ReminderStore

_DATE_FMT = "%Y-%m-%dT%H:%M:%S"


def _entry_to_dict(reminder: Reminder) -> Dict[str, Any]:
    return {
        "expression": reminder.expression,
        "message": reminder.message,
        "due": reminder.due.strftime(_DATE_FMT),
        "label": reminder.label or "",
    }


def _entry_from_dict(data: Dict[str, Any]) -> Reminder:
    return Reminder(
        expression=data["expression"],
        message=data["message"],
        due=datetime.strptime(data["due"], _DATE_FMT),
        label=data.get("label") or None,
    )


def to_json(store: ReminderStore) -> str:
    rows: List[Dict[str, Any]] = [_entry_to_dict(r) for r in store.all()]
    return json.dumps(rows, indent=2)


def from_json(raw: str) -> ReminderStore:
    store = ReminderStore()
    rows = json.loads(raw)
    for item in rows:
        reminder = _entry_from_dict(item)
        store._reminders.append(reminder)
    return store


def to_text(store: ReminderStore) -> str:
    reminders = store.all()
    if not reminders:
        return "No reminders."
    lines = [str(r) for r in reminders]
    return "\n".join(lines)
