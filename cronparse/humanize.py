"""Human-readable descriptions for cron expressions."""

from typing import List
from .parser import CronExpression

_MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

_WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def _describe_values(values: List[int], names: List[str] = None) -> str:
    """Turn a list of integers into a readable enumeration."""
    if names:
        labels = [names[v] for v in values]
    else:
        labels = [str(v) for v in values]
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + " and " + labels[-1]


def humanize(expression: str) -> str:
    """Return a human-readable description of a cron expression.

    Args:
        expression: A standard 5-field cron expression string.

    Returns:
        A plain-English sentence describing the schedule.
    """
    cron = CronExpression(expression)

    minute_vals = cron.minute.values
    hour_vals = cron.hour.values
    day_vals = cron.day.values
    month_vals = cron.month.values
    weekday_vals = cron.weekday.values

    # Time part
    if len(minute_vals) == 60 and len(hour_vals) == 24:
        time_desc = "every minute"
    elif len(minute_vals) == 60:
        time_desc = f"every minute of hour(s) {_describe_values(hour_vals)}"
    elif len(hour_vals) == 24:
        time_desc = f"at minute {_describe_values(minute_vals)} of every hour"
    else:
        times = [
            f"{h:02d}:{m:02d}" for h in hour_vals for m in minute_vals
        ]
        time_desc = "at " + _describe_values(times)

    # Day / weekday part
    all_days = len(day_vals) == 31
    all_weekdays = len(weekday_vals) == 7

    if all_days and all_weekdays:
        day_desc = "every day"
    elif not all_weekdays:
        day_desc = "on " + _describe_values(weekday_vals, _WEEKDAY_NAMES)
    else:
        day_desc = "on day(s) " + _describe_values(day_vals) + " of the month"

    # Month part
    if len(month_vals) == 12:
        month_desc = ""
    else:
        month_desc = " in " + _describe_values(month_vals, _MONTH_NAMES)

    return f"Runs {time_desc}, {day_desc}{month_desc}."
