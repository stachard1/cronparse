"""Generate status badge data for cron expressions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .validator import validate
from .humanize import humanize
from .lint import lint


@dataclass
class Badge:
    """Represents a status badge for a cron expression."""

    expression: str
    label: str
    status: str          # 'valid' | 'warning' | 'invalid'
    color: str           # 'brightgreen' | 'yellow' | 'red'
    message: str

    def __str__(self) -> str:
        return f"[{self.label}: {self.message}] ({self.status})"

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "label": self.label,
            "status": self.status,
            "color": self.color,
            "message": self.message,
        }

    def to_shields_url(self, style: str = "flat") -> str:
        """Return a shields.io badge URL."""
        import urllib.parse

        label = urllib.parse.quote(self.label)
        message = urllib.parse.quote(self.message)
        return (
            f"https://img.shields.io/badge/{label}-{message}-{self.color}"
            f"?style={style}"
        )


def generate_badge(
    expression: str,
    label: Optional[str] = None,
) -> Badge:
    """Generate a Badge for the given cron expression.

    Status rules:
    - invalid  -> red
    - warnings -> yellow
    - clean    -> brightgreen
    """
    result = validate(expression)

    if not result.valid:
        return Badge(
            expression=expression,
            label=label or "cron",
            status="invalid",
            color="red",
            message="invalid",
        )

    lint_result = lint(expression)
    description = humanize(expression)

    if lint_result.warnings:
        return Badge(
            expression=expression,
            label=label or "cron",
            status="warning",
            color="yellow",
            message=description,
        )

    return Badge(
        expression=expression,
        label=label or "cron",
        status="valid",
        color="brightgreen",
        message=description,
    )
