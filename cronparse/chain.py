"""Chain scheduling: define ordered sequences of cron jobs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.exceptions import CronParseError
from cronparse.parser import CronExpression


@dataclass
class ChainStep:
    """A single step in a cron chain."""

    expression: str
    label: str = ""
    delay_minutes: int = 0  # delay after previous step fires

    def __str__(self) -> str:
        parts = [self.expression]
        if self.label:
            parts.append(f"({self.label})")
        if self.delay_minutes:
            parts.append(f"+{self.delay_minutes}m")
        return " ".join(parts)


@dataclass
class CronChain:
    """An ordered sequence of cron job steps."""

    name: str
    steps: List[ChainStep] = field(default_factory=list)

    def add(self, expression: str, label: str = "", delay_minutes: int = 0) -> ChainStep:
        """Add a validated step to the chain."""
        if delay_minutes < 0:
            raise ValueError("delay_minutes must be >= 0")
        try:
            CronExpression(expression)
        except Exception as exc:
            raise CronParseError(f"Invalid expression '{expression}': {exc}") from exc
        step = ChainStep(
            expression=expression,
            label=label.strip(),
            delay_minutes=delay_minutes,
        )
        self.steps.append(step)
        return step

    def remove(self, index: int) -> None:
        """Remove a step by zero-based index."""
        if index < 0 or index >= len(self.steps):
            raise IndexError(f"Step index {index} out of range")
        self.steps.pop(index)

    def reorder(self, from_index: int, to_index: int) -> None:
        """Move a step from one position to another."""
        if not (0 <= from_index < len(self.steps)):
            raise IndexError(f"from_index {from_index} out of range")
        if not (0 <= to_index < len(self.steps)):
            raise IndexError(f"to_index {to_index} out of range")
        step = self.steps.pop(from_index)
        self.steps.insert(to_index, step)

    def summary(self) -> str:
        """Return a human-readable summary of the chain."""
        if not self.steps:
            return f"Chain '{self.name}': (empty)"
        lines = [f"Chain '{self.name}':"]
        for i, step in enumerate(self.steps):
            lines.append(f"  {i + 1}. {step}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.steps)
