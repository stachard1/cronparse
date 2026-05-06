"""Formats cron expressions and their next-run previews into structured output."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from cronparse.parser import CronExpression
from cronparse.humanize import humanize
from cronparse.next_run import next_run
from cronparse.validator import validate


@dataclass
class CronSummary:
    """Structured summary of a cron expression."""
    expression: str
    description: str
    is_valid: bool
    validation_message: str
    next_runs: List[datetime]

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "description": self.description,
            "is_valid": self.is_valid,
            "validation_message": self.validation_message,
            "next_runs": [dt.isoformat() for dt in self.next_runs],
        }

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Description: {self.description}",
            f"Valid      : {self.is_valid}",
        ]
        if not self.is_valid:
            lines.append(f"Error      : {self.validation_message}")
        if self.next_runs:
            lines.append("Next runs  :")
            for dt in self.next_runs:
                lines.append(f"  - {dt.strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)


def summarize(
    expression: str,
    from_dt: Optional[datetime] = None,
    count: int = 5,
) -> CronSummary:
    """Return a CronSummary for the given cron expression string."""
    result = validate(expression)
    description = ""
    runs: List[datetime] = []

    if result.valid:
        try:
            parsed = CronExpression(expression)
            description = humanize(parsed)
            runs = next_run(parsed, from_dt=from_dt, count=count)
        except Exception as exc:  # pragma: no cover
            description = "(error generating description)"

    return CronSummary(
        expression=expression,
        description=description,
        is_valid=result.valid,
        validation_message=str(result),
        next_runs=runs,
    )
