"""JSON serialisation helpers for PriorityQueue."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.priority import PriorityEntry, PriorityLevel, PriorityQueue


def _entry_to_dict(entry: PriorityEntry) -> Dict[str, Any]:
    return {
        "expression": entry.expression,
        "level": entry.level.value,
        "label": entry.label,
    }


def _entry_from_dict(data: Dict[str, Any]) -> PriorityEntry:
    return PriorityEntry(
        expression=data["expression"],
        level=PriorityLevel(data["level"]),
        label=data.get("label", ""),
    )


def to_json(queue: PriorityQueue) -> str:
    rows = [_entry_to_dict(e) for e in queue.get()]
    return json.dumps(rows, indent=2)


def from_json(raw: str) -> PriorityQueue:
    queue: PriorityQueue = PriorityQueue()
    for item in json.loads(raw):
        entry = _entry_from_dict(item)
        queue._entries.append(entry)
    return queue


def to_text(queue: PriorityQueue) -> str:
    entries = queue.get()
    if not entries:
        return "No entries."
    lines = [str(e) for e in entries]
    return "\n".join(lines)
