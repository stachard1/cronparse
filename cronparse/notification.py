"""Notification rule management for cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.validator import validate
from cronparse.exceptions import CronParseError


@dataclass
class NotificationRule:
    expression: str
    channel: str
    label: Optional[str] = None
    enabled: bool = True

    def __str__(self) -> str:
        status = "on" if self.enabled else "off"
        label_part = f" [{self.label}]" if self.label else ""
        return f"{self.expression}{label_part} -> {self.channel} ({status})"


class NotificationStore:
    def __init__(self) -> None:
        self._rules: List[NotificationRule] = []

    def add(
        self,
        expression: str,
        channel: str,
        label: Optional[str] = None,
        enabled: bool = True,
    ) -> NotificationRule:
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression: {result.error}")
        channel = channel.strip()
        if not channel:
            raise ValueError("channel must not be empty")
        rule = NotificationRule(
            expression=expression,
            channel=channel,
            label=label.strip() if label else None,
            enabled=enabled,
        )
        self._rules.append(rule)
        return rule

    def remove(self, expression: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.expression != expression]
        return len(self._rules) < before

    def enable(self, expression: str) -> bool:
        for rule in self._rules:
            if rule.expression == expression:
                rule.enabled = True
                return True
        return False

    def disable(self, expression: str) -> bool:
        for rule in self._rules:
            if rule.expression == expression:
                rule.enabled = False
                return True
        return False

    def active(self) -> List[NotificationRule]:
        return [r for r in self._rules if r.enabled]

    def all(self) -> List[NotificationRule]:
        return list(self._rules)

    def by_channel(self, channel: str) -> List[NotificationRule]:
        return [r for r in self._rules if r.channel == channel]
