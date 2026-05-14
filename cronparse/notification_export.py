"""JSON serialisation for NotificationStore."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.notification import NotificationRule, NotificationStore


def _rule_to_dict(rule: NotificationRule) -> Dict[str, Any]:
    return {
        "expression": rule.expression,
        "channel": rule.channel,
        "label": rule.label or "",
        "enabled": rule.enabled,
    }


def _rule_from_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "expression": data["expression"],
        "channel": data["channel"],
        "label": data.get("label") or None,
        "enabled": bool(data.get("enabled", True)),
    }


def to_json(store: NotificationStore) -> str:
    rows = [_rule_to_dict(r) for r in store.all()]
    return json.dumps(rows, indent=2)


def from_json(raw: str) -> NotificationStore:
    store = NotificationStore()
    for item in json.loads(raw):
        kwargs = _rule_from_dict(item)
        store.add(
            expression=kwargs["expression"],
            channel=kwargs["channel"],
            label=kwargs["label"],
            enabled=kwargs["enabled"],
        )
    return store


def to_text(store: NotificationStore) -> str:
    rules = store.all()
    if not rules:
        return "No notification rules defined."
    lines = [str(r) for r in rules]
    return "\n".join(lines)
