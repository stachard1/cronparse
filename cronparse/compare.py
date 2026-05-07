"""Side-by-side comparison of two cron expressions with field-level analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.parser import CronExpression
from cronparse.humanize import humanize
from cronparse.validator import validate


@dataclass
class FieldComparison:
    field_name: str
    left: str
    right: str
    match: bool

    def __str__(self) -> str:
        status = "=" if self.match else "≠"
        return f"{self.field_name:12s} {status}  {self.left!r:20s} vs {self.right!r}"


@dataclass
class CompareResult:
    left_expr: str
    right_expr: str
    left_valid: bool
    right_valid: bool
    fields: List[FieldComparison] = field(default_factory=list)
    left_human: Optional[str] = None
    right_human: Optional[str] = None

    @property
    def identical(self) -> bool:
        return all(f.match for f in self.fields)

    @property
    def differing_fields(self) -> List[FieldComparison]:
        return [f for f in self.fields if not f.match]

    def __str__(self) -> str:
        lines = [
            f"Left : {self.left_expr}",
            f"Right: {self.right_expr}",
            "",
        ]
        for fc in self.fields:
            lines.append(str(fc))
        lines.append("")
        if self.identical:
            lines.append("Expressions are identical.")
        else:
            lines.append(f"{len(self.differing_fields)} field(s) differ.")
        if self.left_human:
            lines.append(f"Left : {self.left_human}")
        if self.right_human:
            lines.append(f"Right: {self.right_human}")
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def compare(left: str, right: str) -> CompareResult:
    """Compare two cron expressions field by field."""
    left_valid = validate(left).valid
    right_valid = validate(right).valid

    result = CompareResult(
        left_expr=left,
        right_expr=right,
        left_valid=left_valid,
        right_valid=right_valid,
    )

    if not (left_valid and right_valid):
        return result

    left_parsed = CronExpression(left)
    right_parsed = CronExpression(right)

    left_parts = left_parsed.expression.split()
    right_parts = right_parsed.expression.split()

    for name, lv, rv in zip(_FIELD_NAMES, left_parts, right_parts):
        result.fields.append(
            FieldComparison(field_name=name, left=lv, right=rv, match=lv == rv)
        )

    result.left_human = humanize(left)
    result.right_human = humanize(right)

    return result
