"""JSON serialisation helpers for RetentionPolicy."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.retention import RetentionPolicy


def _policy_to_dict(policy: RetentionPolicy) -> Dict[str, Any]:
    return {
        "label": policy.label,
        "max_entries": policy.max_entries,
        "max_age_days": policy.max_age_days,
    }


def _policy_from_dict(data: Dict[str, Any]) -> RetentionPolicy:
    return RetentionPolicy(
        label=data.get("label", ""),
        max_entries=data.get("max_entries"),
        max_age_days=data.get("max_age_days"),
    )


def to_json(policies: List[RetentionPolicy]) -> str:
    """Serialise a list of *RetentionPolicy* objects to a JSON string."""
    return json.dumps([_policy_to_dict(p) for p in policies], indent=2)


def from_json(raw: str) -> List[RetentionPolicy]:
    """Deserialise a JSON string produced by :func:`to_json`."""
    data = json.loads(raw)
    return [_policy_from_dict(d) for d in data]


def to_text(policies: List[RetentionPolicy]) -> str:
    """Return a human-readable summary of *policies*."""
    if not policies:
        return "No retention policies defined."
    lines = []
    for i, p in enumerate(policies, 1):
        label_part = f" [{p.label}]" if p.label else ""
        lines.append(f"{i}.{label_part} {p}")
    return "\n".join(lines)
