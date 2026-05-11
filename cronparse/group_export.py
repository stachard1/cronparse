"""JSON serialisation helpers for GroupRegistry."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.group import CronGroup, GroupRegistry


def _group_to_dict(group: CronGroup) -> Dict[str, Any]:
    return {
        "name": group.name,
        "entries": [
            {"expression": e.expression, "label": e.label or ""}
            for e in group.entries()
        ],
    }


def _group_from_dict(data: Dict[str, Any]) -> CronGroup:
    from cronparse.group import CronGroup
    group = CronGroup(name=data["name"])
    for item in data.get("entries", []):
        group.add(
            expression=item["expression"],
            label=item.get("label") or None,
        )
    return group


def to_json(registry: GroupRegistry) -> str:
    payload = [_group_to_dict(g) for g in registry.all()]
    return json.dumps(payload, indent=2)


def from_json(raw: str) -> GroupRegistry:
    registry = GroupRegistry()
    data = json.loads(raw)
    for item in data:
        group = _group_from_dict(item)
        registry._groups[group.name] = group
    return registry
