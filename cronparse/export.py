"""Export utilities — render a CronHistory to plain text or CSV."""

from __future__ import annotations

import csv
import io
from typing import List

from cronparse.history import CronHistory, HistoryEntry
from cronparse.humanize import humanize


def _entry_rows(entries: List[HistoryEntry], human: bool) -> List[List[str]]:
    rows = []
    for entry in entries:
        description = humanize(entry.expression) if human else ""
        rows.append(
            [
                entry.expression,
                entry.label or "",
                entry.added_at.isoformat(timespec="seconds"),
                description,
            ]
        )
    return rows


def to_csv(history: CronHistory, human: bool = True) -> str:
    """Serialise *history* to a CSV string.

    Columns: ``expression``, ``label``, ``added_at``, ``description``.

    Args:
        history: The history to export.
        human: When *True* (default) include a human-readable description column.

    Returns:
        A UTF-8 CSV string including a header row.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["expression", "label", "added_at", "description"])
    writer.writerows(_entry_rows(history.entries, human))
    return buf.getvalue()


def to_text(history: CronHistory, human: bool = True) -> str:
    """Serialise *history* to a human-readable plain-text string.

    Args:
        history: The history to export.
        human: When *True* (default) append the human-readable description.

    Returns:
        A multi-line string, one entry per line.
    """
    lines: List[str] = []
    for entry in history.entries:
        parts = [entry.expression]
        if entry.label:
            parts.append(f"[{entry.label}]")
        parts.append(f"(added {entry.added_at.isoformat(timespec='seconds')}Z)")
        if human:
            parts.append(f"— {humanize(entry.expression)}")
        lines.append(" ".join(parts))
    return "\n".join(lines)
