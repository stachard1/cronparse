"""Serialise / deserialise a DependencyGraph to/from JSON."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cronparse.dependency import DependencyGraph


def _entry_to_dict(entry) -> dict:
    return {
        "name": entry.name,
        "expression": entry.expression,
        "depends_on": list(entry.depends_on),
        "description": entry.description,
    }


def _entry_from_dict(data: dict):
    return data  # raw dict; graph.add() handles construction


def to_json(graph: "DependencyGraph", indent: int = 2) -> str:
    """Serialise the entire graph to a JSON string."""
    rows = [_entry_to_dict(e) for e in graph.all()]
    return json.dumps(rows, indent=indent)


def from_json(json_str: str, graph: "DependencyGraph") -> "DependencyGraph":
    """Populate *graph* from a JSON string produced by :func:`to_json`."""
    rows = json.loads(json_str)
    for row in rows:
        graph.add(
            name=row["name"],
            expression=row["expression"],
            depends_on=row.get("depends_on", []),
            description=row.get("description", ""),
        )
    return graph


def to_text(graph: "DependencyGraph") -> str:
    """Return a human-readable plain-text summary of the graph."""
    entries = graph.all()
    if not entries:
        return "No jobs registered."
    lines = []
    for e in entries:
        lines.append(str(e))
        if e.description:
            lines.append(f"  {e.description}")
    return "\n".join(lines)
