"""JSON / text export for LockStore."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.lock import LockEntry, LockStore


def _entry_to_dict(entry: LockEntry) -> Dict[str, Any]:
    return {
        "expression": entry.expression,
        "owner": entry.owner,
        "acquired_at": entry.acquired_at.isoformat(),
        "note": entry.note,
    }


def _entry_from_dict(data: Dict[str, Any]) -> dict:
    """Return kwargs suitable for LockStore.acquire (acquired_at is ignored on re-import)."""
    return {
        "expression": data["expression"],
        "owner": data["owner"],
        "note": data.get("note", ""),
    }


def to_json(store: LockStore, *, indent: int = 2) -> str:
    rows: List[Dict[str, Any]] = [_entry_to_dict(e) for e in store.all()]
    return json.dumps(rows, indent=indent)


def from_json(data: str) -> LockStore:
    store = LockStore()
    rows = json.loads(data)
    for row in rows:
        kwargs = _entry_from_dict(row)
        store.acquire(**kwargs)
    return store


def to_text(store: LockStore) -> str:
    entries = store.all()
    if not entries:
        return "No active locks."
    lines = [str(e) for e in entries]
    return "\n".join(lines)
