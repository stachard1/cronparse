"""Suggest cron expressions based on a plain-English description."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Suggestion:
    expression: str
    description: str

    def __str__(self) -> str:
        return f"{self.expression!r:25s}  # {self.description}"


_BUILTIN: List[Suggestion] = [
    Suggestion("* * * * *",   "every minute"),
    Suggestion("0 * * * *",   "every hour, on the hour"),
    Suggestion("0 0 * * *",   "every day at midnight"),
    Suggestion("0 12 * * *",  "every day at noon"),
    Suggestion("0 6 * * *",   "every day at 6 AM"),
    Suggestion("0 18 * * *",  "every day at 6 PM"),
    Suggestion("0 0 * * 0",   "every Sunday at midnight"),
    Suggestion("0 0 * * 1",   "every Monday at midnight"),
    Suggestion("0 0 1 * *",   "first day of every month at midnight"),
    Suggestion("0 0 1 1 *",   "first day of January at midnight (yearly)"),
    Suggestion("*/5 * * * *", "every 5 minutes"),
    Suggestion("*/10 * * * *","every 10 minutes"),
    Suggestion("*/15 * * * *","every 15 minutes"),
    Suggestion("*/30 * * * *","every 30 minutes"),
    Suggestion("0 */2 * * *", "every 2 hours"),
    Suggestion("0 9-17 * * 1-5", "every hour, 9 AM–5 PM, weekdays"),
    Suggestion("0 0 * * 1-5", "every weekday at midnight"),
    Suggestion("0 0 * * 6,0", "every weekend at midnight"),
    Suggestion("0 2 * * *",   "every day at 2 AM (common for backups)"),
    Suggestion("30 23 * * *", "every day at 11:30 PM"),
]


def suggest(query: str, max_results: int = 5) -> List[Suggestion]:
    """Return up to *max_results* suggestions whose description contains all
    words from *query* (case-insensitive).

    If *query* is empty every built-in suggestion is returned (up to
    *max_results*).
    """
    if max_results < 1:
        raise ValueError("max_results must be at least 1")

    words = query.lower().split()

    results: List[Suggestion] = []
    for suggestion in _BUILTIN:
        haystack = suggestion.description.lower()
        if all(w in haystack for w in words):
            results.append(suggestion)
        if len(results) == max_results:
            break

    return results
