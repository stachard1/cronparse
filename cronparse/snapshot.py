"""Snapshot and restore cron expression history sessions."""

import json
from datetime import datetime
from typing import Any, Dict, List

from cronparse.history import CronHistory, HistoryEntry


DATETIME_FMT = "%Y-%m-%dT%H:%M:%S"


def dump(history: CronHistory) -> List[Dict[str, Any]]:
    """Serialize a CronHistory to a list of dicts."""
    return [
        {
            "expression": entry.expression,
            "label": entry.label,
            "added_at": entry.added_at.strftime(DATETIME_FMT),
        }
        for entry in history.entries
    ]


def load(data: List[Dict[str, Any]]) -> CronHistory:
    """Deserialize a list of dicts into a CronHistory (skips invalid entries)."""
    history = CronHistory()
    for item in data:
        try:
            entry = HistoryEntry(
                expression=item["expression"],
                label=item.get("label"),
                added_at=datetime.strptime(item["added_at"], DATETIME_FMT),
            )
            history.entries.append(entry)
        except (KeyError, ValueError):
            continue
    return history


def to_json(history: CronHistory) -> str:
    """Serialize a CronHistory to a JSON string."""
    return json.dumps(dump(history), indent=2)


def from_json(raw: str) -> CronHistory:
    """Deserialize a CronHistory from a JSON string."""
    data = json.loads(raw)
    return load(data)
