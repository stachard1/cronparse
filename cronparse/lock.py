"""Exclusive cron expression locking — prevent concurrent modification."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.parser import CronExpression


@dataclass
class LockEntry:
    expression: str
    owner: str
    acquired_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note: str = ""

    def __str__(self) -> str:  # pragma: no cover
        ts = self.acquired_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        note_part = f" — {self.note}" if self.note else ""
        return f"[LOCKED] {self.expression} (owner={self.owner}, since={ts}{note_part})"


class LockConflictError(Exception):
    """Raised when an expression is already locked by another owner."""


class LockStore:
    """In-memory store for expression locks."""

    def __init__(self) -> None:
        self._locks: Dict[str, LockEntry] = {}

    def acquire(self, expression: str, owner: str, note: str = "") -> LockEntry:
        """Lock *expression* for *owner*. Raises if already locked by someone else."""
        try:
            CronExpression(expression)
        except Exception as exc:
            raise CronParseError(f"Invalid expression: {expression}") from exc

        existing = self._locks.get(expression)
        if existing is not None and existing.owner != owner:
            raise LockConflictError(
                f"Expression '{expression}' is already locked by '{existing.owner}'."
            )

        entry = LockEntry(expression=expression, owner=owner, note=note)
        self._locks[expression] = entry
        return entry

    def release(self, expression: str, owner: str) -> bool:
        """Release the lock. Returns True if released, False if not held."""
        entry = self._locks.get(expression)
        if entry is None:
            return False
        if entry.owner != owner:
            raise LockConflictError(
                f"Cannot release lock on '{expression}': owned by '{entry.owner}'."
            )
        del self._locks[expression]
        return True

    def release_all(self, owner: str) -> int:
        """Release all locks held by *owner*. Returns the number of locks released."""
        expressions = [e.expression for e in self._locks.values() if e.owner == owner]
        for expression in expressions:
            del self._locks[expression]
        return len(expressions)

    def is_locked(self, expression: str) -> bool:
        return expression in self._locks

    def get(self, expression: str) -> Optional[LockEntry]:
        return self._locks.get(expression)

    def all(self) -> List[LockEntry]:
        return list(self._locks.values())

    def held_by(self, owner: str) -> List[LockEntry]:
        return [e for e in self._locks.values() if e.owner == owner]
