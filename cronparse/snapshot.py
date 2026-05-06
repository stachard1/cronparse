"""Persistence helpers: dump/load CronHistory to JSON, with tag support."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from cronparse.history import CronHistory
from cronparse.tags import TagIndex


def dump(history: CronHistory, tag_index: TagIndex | None = None) -> List[Dict[str, Any]]:
    """Serialise history entries to a list of dicts."""
    records = []
    for entry in history.entries:
        record: Dict[str, Any] = {
            "expression": entry.expression,
            "label": entry.label,
            "added_at": entry.added_at.isoformat(),
        }
        if tag_index is not None:
            record["tags"] = tag_index.tags_for(entry.expression)
        records.append(record)
    return records


def load(records: List[Dict[str, Any]]) -> tuple[CronHistory, TagIndex]:
    """Deserialise history entries and rebuild a TagIndex."""
    history = CronHistory()
    tag_index = TagIndex()
    for record in records:
        history.add(record["expression"], label=record.get("label"))
        for tag in record.get("tags", []):
            tag_index.add(tag, record["expression"])
    return history, tag_index


def to_json(
    history: CronHistory,
    tag_index: TagIndex | None = None,
    indent: int = 2,
) -> str:
    """Serialise history (and optional tags) to a JSON string."""
    return json.dumps(dump(history, tag_index), indent=indent)


def from_json(raw: str) -> tuple[CronHistory, TagIndex]:
    """Deserialise history and tags from a JSON string."""
    return load(json.loads(raw))
