"""Named alias registry for cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.parser import CronExpression


@dataclass
class AliasEntry:
    name: str
    expression: str
    description: str = ""

    def __str__(self) -> str:
        parts = [f"{self.name}: {self.expression}"]
        if self.description:
            parts.append(f"  # {self.description}")
        return "".join(parts)


class AliasRegistry:
    """Stores named aliases for cron expressions."""

    def __init__(self) -> None:
        self._entries: Dict[str, AliasEntry] = {}

    def register(self, name: str, expression: str, description: str = "") -> AliasEntry:
        """Register a named alias. Raises CronParseError if expression is invalid."""
        name = name.strip()
        if not name:
            raise ValueError("Alias name must not be empty.")
        try:
            CronExpression.parse(expression)
        except Exception as exc:
            raise CronParseError(f"Invalid expression for alias '{name}': {exc}") from exc
        entry = AliasEntry(name=name, expression=expression, description=description.strip())
        self._entries[name] = entry
        return entry

    def get(self, name: str) -> Optional[AliasEntry]:
        """Return the alias entry for *name*, or None."""
        return self._entries.get(name)

    def remove(self, name: str) -> bool:
        """Remove an alias by name. Returns True if it existed."""
        if name in self._entries:
            del self._entries[name]
            return True
        return False

    def all(self) -> List[AliasEntry]:
        """Return all registered aliases sorted by name."""
        return sorted(self._entries.values(), key=lambda e: e.name)

    def __iter__(self) -> Iterator[AliasEntry]:
        return iter(self.all())

    def __len__(self) -> int:
        return len(self._entries)
