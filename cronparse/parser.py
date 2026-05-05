"""Core cron expression parser and validator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .exceptions import CronParseError, CronFieldError

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),  # 0 and 7 both represent Sunday
}
MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    name: str
    raw: str
    values: set[int] = field(default_factory=set)


@dataclass
class CronExpression:
    """Represents a parsed and validated cron expression."""

    raw: str
    fields: dict[str, CronField] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._parse()

    def _resolve_alias(self, value: str, field_name: str) -> str:
        lower = value.lower()
        if field_name == "month" and lower in MONTH_ALIASES:
            return str(MONTH_ALIASES[lower])
        if field_name == "day_of_week" and lower in DOW_ALIASES:
            return str(DOW_ALIASES[lower])
        return value

    def _parse_value(self, token: str, field_name: str) -> set[int]:
        lo, hi = FIELD_RANGES[field_name]
        token = self._resolve_alias(token, field_name)

        if token == "*":
            return set(range(lo, hi + 1))

        if "/" in token:
            base, step_str = token.split("/", 1)
            if not step_str.isdigit():
                raise CronFieldError(self.raw, field_name, token, "step must be an integer")
            step = int(step_str)
            if step == 0:
                raise CronFieldError(self.raw, field_name, token, "step cannot be zero")
            start = lo if base == "*" else int(self._resolve_alias(base, field_name))
            return set(range(start, hi + 1, step))

        if "-" in token:
            parts = token.split("-", 1)
            start, end = int(self._resolve_alias(parts[0], field_name)), int(self._resolve_alias(parts[1], field_name))
            if start > end:
                raise CronFieldError(self.raw, field_name, token, "range start exceeds end")
            return set(range(start, end + 1))

        if token.isdigit():
            return {int(token)}

        raise CronFieldError(self.raw, field_name, token, "unrecognised token")

    def _parse_field(self, raw: str, field_name: str) -> CronField:
        lo, hi = FIELD_RANGES[field_name]
        values: set[int] = set()
        for part in raw.split(","):
            part_values = self._parse_value(part.strip(), field_name)
            out_of_range = {v for v in part_values if not (lo <= v <= hi)}
            if out_of_range:
                raise CronFieldError(self.raw, field_name, raw, f"values out of range [{lo}-{hi}]: {out_of_range}")
            values |= part_values
        return CronField(name=field_name, raw=raw, values=values)

    def _parse(self) -> None:
        parts = self.raw.strip().split()
        if len(parts) != 5:
            raise CronParseError(self.raw, f"expected 5 fields, got {len(parts)}")
        for name, raw in zip(FIELD_NAMES, parts):
            self.fields[name] = self._parse_field(raw, name)

    @property
    def minute(self) -> set[int]:
        return self.fields["minute"].values

    @property
    def hour(self) -> set[int]:
        return self.fields["hour"].values

    @property
    def day_of_month(self) -> set[int]:
        return self.fields["day_of_month"].values

    @property
    def month(self) -> set[int]:
        return self.fields["month"].values

    @property
    def day_of_week(self) -> set[int]:
        return self.fields["day_of_week"].values

    def __repr__(self) -> str:  # pragma: no cover
        return f"CronExpression({self.raw!r})"
