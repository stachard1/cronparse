"""Throttle rules: prevent a cron job from running more than N times in a window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.validator import validate


@dataclass
class ThrottleRule:
    expression: str
    max_runs: int
    window_seconds: int
    label: str = ""

    def __str__(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        window = timedelta(seconds=self.window_seconds)
        return (
            f"ThrottleRule{label_part}: '{self.expression}' "
            f"max {self.max_runs} runs per {window}"
        )

    @property
    def window(self) -> timedelta:
        return timedelta(seconds=self.window_seconds)


@dataclass
class ThrottleCheckResult:
    rule: ThrottleRule
    run_count: int
    allowed: bool

    def __str__(self) -> str:
        status = "allowed" if self.allowed else "throttled"
        return (
            f"{status}: {self.run_count}/{self.rule.max_runs} runs "
            f"in {self.rule.window}"
        )


class ThrottleStore:
    def __init__(self) -> None:
        self._rules: List[ThrottleRule] = []

    def add(
        self,
        expression: str,
        max_runs: int,
        window_seconds: int,
        label: str = "",
    ) -> ThrottleRule:
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression: {result.error}")
        if max_runs < 1:
            raise ValueError("max_runs must be >= 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")
        rule = ThrottleRule(
            expression=expression,
            max_runs=max_runs,
            window_seconds=window_seconds,
            label=label.strip(),
        )
        self._rules.append(rule)
        return rule

    def remove(self, expression: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.expression != expression]
        return len(self._rules) < before

    def get(self, expression: str) -> Optional[ThrottleRule]:
        for rule in self._rules:
            if rule.expression == expression:
                return rule
        return None

    def all(self) -> List[ThrottleRule]:
        return list(self._rules)

    def check(self, expression: str, run_count: int) -> Optional[ThrottleCheckResult]:
        rule = self.get(expression)
        if rule is None:
            return None
        allowed = run_count <= rule.max_runs
        return ThrottleCheckResult(rule=rule, run_count=run_count, allowed=allowed)
