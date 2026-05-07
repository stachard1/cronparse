"""Cron expression linter — detects suspicious or non-portable patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression
from .validator import validate


@dataclass
class LintWarning:
    field: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.field}: {self.message}"


@dataclass
class LintResult:
    expression: str
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        if self.clean:
            return f"{self.expression}: OK"
        lines = [f"{self.expression}: {len(self.warnings)} warning(s)"]
        lines.extend(f"  {w}" for w in self.warnings)
        return "\n".join(lines)


_RULES = []


def _rule(fn):
    _RULES.append(fn)
    return fn


@_rule
def _check_leap_day(expr: CronExpression, warnings: List[LintWarning]) -> None:
    """Warn when day-of-month is 29 and month is 2 (Feb 29 is rare)."""
    dom_vals = expr.day_of_month.values
    month_vals = expr.month.values
    if 29 in dom_vals and 2 in month_vals and len(month_vals) == 1:
        warnings.append(LintWarning(
            field="day_of_month",
            code="W001",
            message="Day 29 in February only exists on leap years.",
        ))


@_rule
def _check_high_frequency(expr: CronExpression, warnings: List[LintWarning]) -> None:
    """Warn when the job runs more often than every minute (step < 1 is impossible,
    but a wildcard on both minute and second-like fields is suspicious)."""
    if expr.minute.values == list(range(60)) and expr.hour.values == list(range(24)):
        warnings.append(LintWarning(
            field="minute",
            code="W002",
            message="Expression runs every minute of every hour — consider a less frequent schedule.",
        ))


@_rule
def _check_dom_and_dow_both_set(expr: CronExpression, warnings: List[LintWarning]) -> None:
    """Warn when both day-of-month and day-of-week are restricted (non-wildcard).
    Many cron implementations OR these fields, which is often surprising."""
    dom_is_wildcard = expr.day_of_month.values == list(range(1, 32))
    dow_is_wildcard = expr.day_of_week.values == list(range(7))
    if not dom_is_wildcard and not dow_is_wildcard:
        warnings.append(LintWarning(
            field="day_of_month/day_of_week",
            code="W003",
            message="Both day-of-month and day-of-week are restricted; most cron daemons OR these fields.",
        ))


def lint(expression: str) -> LintResult:
    """Lint *expression* and return a :class:`LintResult` with any warnings."""
    result = validate(expression)
    if not result.valid:
        # Return empty lint result — validation errors take precedence.
        return LintResult(expression=expression, warnings=[])

    expr = CronExpression(expression)
    warnings: List[LintWarning] = []
    for rule in _RULES:
        rule(expr, warnings)
    return LintResult(expression=expression, warnings=warnings)
