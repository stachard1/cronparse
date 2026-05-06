"""Search and filter utilities for CronHistory entries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from cronparse.history import CronHistory, HistoryEntry
from cronparse.tags import TagIndex


@dataclass
class SearchQuery:
    """Parameters for filtering history entries."""

    label: Optional[str] = None
    tag: Optional[str] = None
    expression_contains: Optional[str] = None

    def is_empty(self) -> bool:
        return all(
            v is None for v in (self.label, self.tag, self.expression_contains)
        )


def search(
    history: CronHistory,
    query: SearchQuery,
    tag_index: Optional[TagIndex] = None,
) -> List[HistoryEntry]:
    """Return history entries matching *all* non-None criteria in *query*.

    Args:
        history: The :class:`CronHistory` to search.
        query: A :class:`SearchQuery` describing the filter criteria.
        tag_index: Optional :class:`TagIndex` used when ``query.tag`` is set.

    Returns:
        A list of matching :class:`HistoryEntry` objects (may be empty).
    """
    if query.is_empty():
        return list(history.entries)

    # Collect expression strings allowed by tag filter first (cheap set lookup).
    tag_allowed: Optional[set] = None
    if query.tag is not None:
        if tag_index is None:
            raise ValueError("tag_index must be provided when filtering by tag")
        tag_allowed = set(tag_index.get(query.tag))

    results: List[HistoryEntry] = []
    for entry in history.entries:
        if query.label is not None:
            if entry.label is None or query.label.lower() not in entry.label.lower():
                continue
        if tag_allowed is not None:
            if entry.expression not in tag_allowed:
                continue
        if query.expression_contains is not None:
            if query.expression_contains not in entry.expression:
                continue
        results.append(entry)

    return results
