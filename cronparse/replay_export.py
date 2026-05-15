"""Serialise and deserialise ReplayResult objects."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from cronparse.replay import ReplayEntry, ReplayResult

_FMT = "%Y-%m-%dT%H:%M:%S"


def _result_to_dict(result: ReplayResult) -> Dict[str, Any]:
    return {
        "expression": result.expression,
        "label": result.label,
        "start": result.start.strftime(_FMT),
        "end": result.end.strftime(_FMT),
        "entries": [
            {
                "expression": e.expression,
                "label": e.label,
                "fired_at": e.fired_at.strftime(_FMT),
            }
            for e in result.entries
        ],
    }


def to_json(result: ReplayResult) -> str:
    """Serialise a ReplayResult to a JSON string."""
    return json.dumps(_result_to_dict(result), indent=2)


def from_json(data: str) -> ReplayResult:
    """Deserialise a ReplayResult from a JSON string."""
    raw = json.loads(data)
    entries = [
        ReplayEntry(
            expression=e["expression"],
            label=e.get("label"),
            fired_at=datetime.strptime(e["fired_at"], _FMT),
        )
        for e in raw.get("entries", [])
    ]
    result = ReplayResult(
        expression=raw["expression"],
        label=raw.get("label"),
        start=datetime.strptime(raw["start"], _FMT),
        end=datetime.strptime(raw["end"], _FMT),
        entries=entries,
    )
    return result


def to_text(result: ReplayResult) -> str:
    """Return a human-readable text summary of a ReplayResult."""
    lines: List[str] = [str(result)]
    for entry in result.entries:
        lines.append(f"  {entry}")
    return "\n".join(lines)
