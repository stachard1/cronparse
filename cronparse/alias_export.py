"""JSON serialisation helpers for AliasRegistry."""

from __future__ import annotations

import json
from typing import List

from cronparse.alias import AliasEntry, AliasRegistry


def _entry_to_dict(entry: AliasEntry) -> dict:
    return {
        "name": entry.name,
        "expression": entry.expression,
        "description": entry.description,
    }


def _entry_from_dict(data: dict) -> tuple:
    """Return (name, expression, description) from a raw dict."""
    return data["name"], data["expression"], data.get("description", "")


def to_json(registry: AliasRegistry, *, indent: int = 2) -> str:
    """Serialise *registry* to a JSON string."""
    payload = [_entry_to_dict(e) for e in registry.all()]
    return json.dumps(payload, indent=indent)


def from_json(raw: str) -> AliasRegistry:
    """Deserialise a JSON string produced by :func:`to_json` into a new registry."""
    registry = AliasRegistry()
    data: List[dict] = json.loads(raw)
    for item in data:
        name, expression, description = _entry_from_dict(item)
        registry.register(name, expression, description)
    return registry
