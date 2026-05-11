"""Pin module: mark cron expressions as pinned/favourites."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.parser import CronExpression


@dataclass
class PinEntry:
    expression: str
    label: str = ""

    def __str__(self) -> str:
        if self.label:
            return f"{self.label}: {self.expression}"
        return self.expression


class PinStore:
    """Stores pinned cron expressions."""

    def __init__(self) -> None:
        self._pins: Dict[str, PinEntry] = {}

    def pin(self, expression: str, label: str = "") -> PinEntry:
        """Pin an expression. Raises CronParseError if invalid."""
        CronExpression(expression)  # validate
        entry = PinEntry(expression=expression, label=label.strip())
        self._pins[expression] = entry
        return entry

    def unpin(self, expression: str) -> bool:
        """Remove a pinned expression. Returns True if it existed."""
        if expression in self._pins:
            del self._pins[expression]
            return True
        return False

    def is_pinned(self, expression: str) -> bool:
        """Return True if the expression is currently pinned."""
        return expression in self._pins

    def all(self) -> List[PinEntry]:
        """Return a copy of all pinned entries."""
        return list(self._pins.values())

    def get(self, expression: str) -> Optional[PinEntry]:
        """Return the PinEntry for an expression, or None."""
        return self._pins.get(expression)

    def clear(self) -> None:
        """Remove all pinned expressions."""
        self._pins.clear()

    def __len__(self) -> int:
        return len(self._pins)
