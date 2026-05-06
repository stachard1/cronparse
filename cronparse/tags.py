"""Tag management for cron expressions stored in history."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError


@dataclass
class TagIndex:
    """Maps tags to lists of cron expressions."""

    _index: Dict[str, List[str]] = field(default_factory=dict)

    def add(self, tag: str, expression: str) -> None:
        """Associate a tag with a cron expression."""
        tag = tag.strip().lower()
        if not tag:
            raise CronParseError("Tag must not be empty.")
        self._index.setdefault(tag, [])
        if expression not in self._index[tag]:
            self._index[tag].append(expression)

    def remove(self, tag: str, expression: Optional[str] = None) -> None:
        """Remove a tag entirely, or just its association with one expression."""
        tag = tag.strip().lower()
        if tag not in self._index:
            return
        if expression is None:
            del self._index[tag]
        else:
            self._index[tag] = [e for e in self._index[tag] if e != expression]
            if not self._index[tag]:
                del self._index[tag]

    def get(self, tag: str) -> List[str]:
        """Return all expressions associated with a tag."""
        return list(self._index.get(tag.strip().lower(), []))

    def tags_for(self, expression: str) -> List[str]:
        """Return all tags associated with a given expression."""
        return [tag for tag, exprs in self._index.items() if expression in exprs]

    def all_tags(self) -> List[str]:
        """Return all known tags."""
        return list(self._index.keys())

    def to_dict(self) -> Dict[str, List[str]]:
        """Serialise the index to a plain dict."""
        return {tag: list(exprs) for tag, exprs in self._index.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, List[str]]) -> "TagIndex":
        """Deserialise a TagIndex from a plain dict."""
        instance = cls()
        for tag, exprs in data.items():
            for expr in exprs:
                instance.add(tag, expr)
        return instance
