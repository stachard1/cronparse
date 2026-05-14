"""JSON / text export and import for ThrottleStore."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.throttle import ThrottleRule, ThrottleStore


def _rule_to_dict(rule: ThrottleRule) -> Dict[str, Any]:
    return {
        "expression": rule.expression,
        "max_runs": rule.max_runs,
        "window_seconds": rule.window_seconds,
        "label": rule.label,
    }


def _rule_from_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "expression": data["expression"],
        "max_runs": int(data["max_runs"]),
        "window_seconds": int(data["window_seconds"]),
        "label": data.get("label", ""),
    }


def to_json(store: ThrottleStore) -> str:
    return json.dumps([_rule_to_dict(r) for r in store.all()], indent=2)


def from_json(raw: str) -> ThrottleStore:
    store = ThrottleStore()
    for item in json.loads(raw):
        kwargs = _rule_from_dict(item)
        store.add(**kwargs)
    return store


def to_text(store: ThrottleStore) -> str:
    rules = store.all()
    if not rules:
        return "No throttle rules defined."
    lines: List[str] = []
    for rule in rules:
        lines.append(str(rule))
    return "\n".join(lines)
