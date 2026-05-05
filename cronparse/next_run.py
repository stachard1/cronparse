"""Next-run preview calculator for cron expressions."""

from datetime import datetime, timedelta
from typing import List, Optional

from .parser import CronExpression
from .exceptions import CronParseError


def _matching_values(field_values: List[int], lo: int, hi: int) -> List[int]:
    """Return sorted list of values from field that fall within [lo, hi]."""
    return sorted(v for v in field_values if lo <= v <= hi)


def next_run(
    expression: str,
    after: Optional[datetime] = None,
    count: int = 1,
) -> List[datetime]:
    """Return the next *count* run times for a cron expression.

    Args:
        expression: A standard 5-field cron expression string.
        after: Start datetime (defaults to now). Results are strictly after this.
        count: Number of next run times to return.

    Returns:
        A list of datetime objects representing the next scheduled runs.

    Raises:
        CronParseError: If the expression is invalid.
        ValueError: If count < 1.
    """
    if count < 1:
        raise ValueError("count must be at least 1")

    cron = CronExpression(expression)
    base = (after or datetime.now()).replace(second=0, microsecond=0)
    current = base + timedelta(minutes=1)

    results: List[datetime] = []
    # Guard against infinite loop — search up to ~4 years ahead
    limit = current + timedelta(days=366 * 4)

    minutes = cron.minute.values
    hours = cron.hour.values
    days = cron.day.values
    months = cron.month.values
    weekdays = cron.weekday.values

    while len(results) < count and current < limit:
        if current.month not in months:
            # Advance to first day of next valid month
            current = _advance_to_next_month(current, months)
            continue

        if current.day not in days or current.weekday() not in weekdays:
            current = current.replace(hour=0, minute=0) + timedelta(days=1)
            continue

        if current.hour not in hours:
            current = current.replace(minute=0) + timedelta(hours=1)
            continue

        if current.minute not in minutes:
            current += timedelta(minutes=1)
            continue

        results.append(current)
        current += timedelta(minutes=1)

    return results


def _advance_to_next_month(dt: datetime, valid_months: List[int]) -> datetime:
    """Advance datetime to the first minute of the next valid month."""
    month = dt.month
    year = dt.year
    for _ in range(24):  # at most 2 years of months
        month += 1
        if month > 12:
            month = 1
            year += 1
        if month in valid_months:
            return datetime(year, month, 1, 0, 0)
    # Fallback: move well past the limit so the caller exits
    return dt + timedelta(days=366 * 5)
