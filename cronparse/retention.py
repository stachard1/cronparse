"""Retention policy management for cron history entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from cronparse.history import CronHistory, HistoryEntry


@dataclass
class RetentionPolicy:
    """Defines how long history entries should be kept."""

    max_entries: Optional[int] = None
    max_age_days: Optional[float] = None
    label: str = ""

    def __str__(self) -> str:
        parts = []
        if self.max_entries is not None:
            parts.append(f"max_entries={self.max_entries}")
        if self.max_age_days is not None:
            parts.append(f"max_age_days={self.max_age_days}")
        if not parts:
            return "RetentionPolicy(keep=all)"
        return f"RetentionPolicy({', '.join(parts)})"

    @property
    def is_unbounded(self) -> bool:
        return self.max_entries is None and self.max_age_days is None


@dataclass
class RetentionResult:
    """Result of applying a retention policy."""

    removed: List[HistoryEntry] = field(default_factory=list)
    kept: List[HistoryEntry] = field(default_factory=list)

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def __str__(self) -> str:
        return (
            f"RetentionResult(kept={self.kept_count}, removed={self.removed_count})"
        )


def apply_retention(history: CronHistory, policy: RetentionPolicy) -> RetentionResult:
    """Apply *policy* to *history*, removing entries that exceed the policy limits.

    Entries are evaluated oldest-first; the most recent entries are preferred
    when *max_entries* is the limiting factor.
    """
    if policy.is_unbounded:
        return RetentionResult(removed=[], kept=list(history.entries))

    entries: List[HistoryEntry] = list(history.entries)
    now = datetime.utcnow()
    to_remove: List[HistoryEntry] = []

    # Age-based pruning
    if policy.max_age_days is not None:
        cutoff = now - timedelta(days=policy.max_age_days)
        for entry in entries:
            if entry.added_at < cutoff:
                to_remove.append(entry)

    surviving = [e for e in entries if e not in to_remove]

    # Count-based pruning (keep the most recent N)
    if policy.max_entries is not None and len(surviving) > policy.max_entries:
        overflow = surviving[: len(surviving) - policy.max_entries]
        to_remove.extend(overflow)
        surviving = surviving[len(overflow):]

    for entry in to_remove:
        try:
            history.remove(entry.expression)
        except Exception:
            pass

    return RetentionResult(removed=to_remove, kept=surviving)
