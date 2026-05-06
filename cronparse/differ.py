"""Diff two cron expressions and describe what changed between them."""

from dataclasses import dataclass
from typing import List, Optional

from cronparse.parser import CronExpression
from cronparse.exceptions import CronParseError


FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


@dataclass
class FieldDiff:
    field: str
    old_value: str
    new_value: str

    def __str__(self) -> str:
        return f"{self.field}: '{self.old_value}' -> '{self.new_value}'"


@dataclass
class CronDiff:
    old_expression: str
    new_expression: str
    changes: List[FieldDiff]

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        if not self.has_changes:
            return "No differences found between expressions."
        lines = [f"Diff: '{self.old_expression}' vs '{self.new_expression}'"] + [
            f"  {c}" for c in self.changes
        ]
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.summary()


def diff(old: str, new: str) -> CronDiff:
    """Compare two cron expressions field by field and return a CronDiff."""
    old_expr = CronExpression(old)
    new_expr = CronExpression(new)

    old_fields = [
        old_expr.minute.raw,
        old_expr.hour.raw,
        old_expr.day_of_month.raw,
        old_expr.month.raw,
        old_expr.day_of_week.raw,
    ]
    new_fields = [
        new_expr.minute.raw,
        new_expr.hour.raw,
        new_expr.day_of_month.raw,
        new_expr.month.raw,
        new_expr.day_of_week.raw,
    ]

    changes = [
        FieldDiff(field=name, old_value=old_val, new_value=new_val)
        for name, old_val, new_val in zip(FIELD_NAMES, old_fields, new_fields)
        if old_val != new_val
    ]

    return CronDiff(
        old_expression=old,
        new_expression=new,
        changes=changes,
    )
