"""JSON / plain-text serialisation for QuotaStore."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.quota import QuotaEntry, QuotaStore


def _entry_to_dict(entry: QuotaEntry) -> Dict[str, Any]:
    return {
        "expression": entry.expression,
        "max_runs": entry.max_runs,
        "window_hours": entry.window_hours,
        "label": entry.label,
    }


def _entry_from_dict(data: Dict[str, Any]) -> QuotaEntry:
    return QuotaEntry(
        expression=data["expression"],
        max_runs=int(data["max_runs"]),
        window_hours=int(data["window_hours"]),
        label=data.get("label", ""),
    )


def to_json(store: QuotaStore) -> str:
    """Serialise a QuotaStore to a JSON string."""
    return json.dumps([_entry_to_dict(e) for e in store.all()], indent=2)


def from_json(raw: str) -> QuotaStore:
    """Deserialise a QuotaStore from a JSON string."""
    store: QuotaStore = QuotaStore()
    for item in json.loads(raw):
        entry = _entry_from_dict(item)
        store._entries.append(entry)
    return store


def to_text(store: QuotaStore) -> str:
    """Return a human-readable summary of all quota entries."""
    entries = store.all()
    if not entries:
        return "No quota entries defined."
    lines: List[str] = []
    for e in entries:
        lbl = f" [{e.label}]" if e.label else ""
        lines.append(
            f"{e.expression}{lbl}: max {e.max_runs} runs / {e.window_hours}h"
        )
    return "\n".join(lines)
