"""Serialise / deserialise a Watchlist to JSON."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from cronparse.watchlist import WatchEntry, Watchlist

_DT_FMT = "%Y-%m-%dT%H:%M:%S.%f"


def _entry_to_dict(entry: WatchEntry) -> Dict[str, Any]:
    return {
        "expression": entry.expression,
        "label": entry.label,
        "added_at": entry.added_at.strftime(_DT_FMT),
        "last_changed": entry.last_changed.strftime(_DT_FMT) if entry.last_changed else None,
    }


def _entry_from_dict(data: Dict[str, Any]) -> WatchEntry:
    last_changed = (
        datetime.strptime(data["last_changed"], _DT_FMT)
        if data.get("last_changed")
        else None
    )
    entry = WatchEntry(
        expression=data["expression"],
        label=data["label"],
        added_at=datetime.strptime(data["added_at"], _DT_FMT),
        last_changed=last_changed,
    )
    return entry


def to_json(watchlist: Watchlist, indent: int = 2) -> str:
    """Serialise *watchlist* to a JSON string."""
    payload: List[Dict[str, Any]] = [_entry_to_dict(e) for e in watchlist.all()]
    return json.dumps(payload, indent=indent)


def from_json(raw: str) -> Watchlist:
    """Reconstruct a :class:`Watchlist` from a JSON string produced by :func:`to_json`."""
    payload = json.loads(raw)
    wl = Watchlist()
    for item in payload:
        entry = _entry_from_dict(item)
        wl._entries[entry.label] = entry  # bypass validation for round-trip
    return wl
