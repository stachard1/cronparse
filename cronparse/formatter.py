"""Summarize a cron expression into a structured CronSummary object."""

from dataclasses import dataclass, field
from typing import List, Optional
import json

from cronparse.parser import CronExpression
from cronparse.validator import validate
from cronparse.humanize import humanize
from cronparse.next_run import next_run
from cronparse.exceptions import CronParseError


@dataclass
class CronSummary:
    expression: str
    is_valid: bool
    human_readable: Optional[str]
    next_runs: List[str]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_valid": self.is_valid,
            "human_readable": self.human_readable,
            "next_runs": self.next_runs,
            "error": self.error,
        }

    def __str__(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Valid      : {self.is_valid}",
        ]
        if self.error:
            lines.append(f"Error      : {self.error}")
        if self.human_readable:
            lines.append(f"Description: {self.human_readable}")
        if self.next_runs:
            lines.append("Next runs  :")
            for run in self.next_runs:
                lines.append(f"  - {run}")
        return "\n".join(lines)


def summarize(expression: str, count: int = 5) -> CronSummary:
    """Build a CronSummary for the given cron expression."""
    result = validate(expression)
    if not result.is_valid:
        return CronSummary(
            expression=expression,
            is_valid=False,
            human_readable=None,
            next_runs=[],
            error=str(result),
        )

    try:
        description = humanize(expression)
    except Exception as exc:  # pragma: no cover
        description = None

    try:
        runs = next_run(expression, count=count)
        formatted_runs = [dt.strftime("%Y-%m-%d %H:%M") for dt in runs]
    except Exception:  # pragma: no cover
        formatted_runs = []

    return CronSummary(
        expression=expression,
        is_valid=True,
        human_readable=description,
        next_runs=formatted_runs,
    )
