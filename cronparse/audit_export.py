"""Serialisation helpers for AuditLog — JSON and plain-text."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.audit import AuditEvent, AuditLog


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _event_to_dict(event: AuditEvent) -> Dict[str, Any]:
    return {
        "expression": event.expression,
        "action": event.action,
        "label": event.label,
        "note": event.note,
        "timestamp": event.timestamp.isoformat(),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def to_json(log: AuditLog, indent: int = 2) -> str:
    """Serialise *log* to a JSON string."""
    payload: List[Dict[str, Any]] = [_event_to_dict(e) for e in log.events()]
    return json.dumps(payload, indent=indent)


def from_json(data: str) -> AuditLog:
    """Reconstruct an :class:`AuditLog` from a JSON string produced by :func:`to_json`."""
    from datetime import datetime, timezone  # local import to keep top clean

    records = json.loads(data)
    log = AuditLog()
    for r in records:
        event = AuditEvent(
            expression=r["expression"],
            action=r["action"],
            label=r.get("label"),
            note=r.get("note"),
            timestamp=datetime.fromisoformat(r["timestamp"]).replace(tzinfo=timezone.utc),
        )
        log._events.append(event)  # noqa: SLF001
    return log


def to_text(log: AuditLog) -> str:
    """Render *log* as a human-readable text block."""
    if not log.events():
        return "(no audit events recorded)"
    return "\n".join(str(e) for e in log.events())
