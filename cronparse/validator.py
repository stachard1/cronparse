"""Validation utilities for cron expressions."""

from dataclasses import dataclass
from typing import List

from cronparse.exceptions import CronParseError, CronFieldError
from cronparse.parser import CronExpression, CronField


@dataclass
class ValidationResult:
    """Result of a cron expression validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __str__(self) -> str:
        if self.is_valid:
            return "Valid cron expression"
        return "Invalid cron expression: " + "; ".join(self.errors)


def validate(expression: str) -> ValidationResult:
    """Validate a cron expression and return a detailed result.

    Args:
        expression: A cron expression string (5 fields).

    Returns:
        A ValidationResult with is_valid flag, errors, and warnings.
    """
    errors: List[str] = []
    warnings: List[str] = []

    parts = expression.strip().split()
    if len(parts) != 5:
        errors.append(
            f"Expected 5 fields, got {len(parts)}. "
            "Format: <minute> <hour> <dom> <month> <dow>"
        )
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    try:
        expr = CronExpression(expression)
    except CronFieldError as exc:
        errors.append(str(exc))
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
    except CronParseError as exc:
        errors.append(str(exc))
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Warn about potentially unintended combinations
    dom_values = set(expr.dom.values)
    dow_values = set(expr.dow.values)

    dom_is_wildcard = dom_values == set(range(1, 32))
    dow_is_wildcard = dow_values == set(range(0, 7))

    if not dom_is_wildcard and not dow_is_wildcard:
        warnings.append(
            "Both day-of-month and day-of-week are restricted; "
            "runs when EITHER condition matches (OR logic)."
        )

    hour_values = set(expr.hour.values)
    if hour_values == set(range(0, 24)) and set(expr.minute.values) == set(range(0, 60)):
        warnings.append(
            "Expression matches every minute — consider whether this is intentional."
        )

    return ValidationResult(is_valid=True, errors=errors, warnings=warnings)
