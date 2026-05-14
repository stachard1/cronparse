"""JSON serialisation helpers for CooldownStore."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.cooldown import CooldownEntry, CooldownStore


def _entry_to_dict(entry: CooldownEntry) -> Dict[str, Any]:
    return {
        "expression": entry.expression,
        "min_interval_seconds": entry.min_interval_seconds,
        "label": entry.label,
    }


def _entry_from_dict(data: Dict[str, Any]) -> CooldownEntry:
    return CooldownEntry(
        expression=data["expression"],
        min_interval_seconds=int(data["min_interval_seconds"]),
        label=data.get("label", ""),
    )


def to_json(store: CooldownStore) -> str:
    """Serialise *store* to a JSON string."""
    return json.dumps([_entry_to_dict(e) for e in store.all()], indent=2)


def from_json(raw: str) -> CooldownStore:
    """Deserialise a CooldownStore from a JSON string produced by :func:`to_json`."""
    store = CooldownStore()
    rows: List[Dict[str, Any]] = json.loads(raw)
    for row in rows:
        entry = _entry_from_dict(row)
        store._entries[entry.expression] = entry
    return store


def to_text(store: CooldownStore) -> str:
    """Return a human-readable summary of all cooldown entries."""
    entries = store.all()
    if not entries:
        return "No cooldown rules registered."
    lines = ["Cooldown Rules", "-" * 40]
    for e in entries:
        label_part = f"  [{e.label}]" if e.label else ""
        lines.append(f"{e.expression}{label_part}  →  min {e.min_interval_seconds}s")
    return "\n".join(lines)
