"""Group multiple cron expressions under a named collection."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.parser import CronExpression
from cronparse.validator import validate


@dataclass
class GroupEntry:
    expression: str
    label: Optional[str] = None

    def __str__(self) -> str:
        tag = f" ({self.label})" if self.label else ""
        return f"{self.expression}{tag}"


@dataclass
class CronGroup:
    name: str
    _entries: List[GroupEntry] = field(default_factory=list, init=False, repr=False)

    def add(self, expression: str, label: Optional[str] = None) -> GroupEntry:
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression '{expression}': {result.reason}")
        entry = GroupEntry(expression=expression, label=label)
        self._entries.append(entry)
        return entry

    def remove(self, expression: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.expression != expression]
        return len(self._entries) < before

    def entries(self) -> List[GroupEntry]:
        return list(self._entries)

    def expressions(self) -> List[str]:
        return [e.expression for e in self._entries]

    def __len__(self) -> int:
        return len(self._entries)

    def __str__(self) -> str:
        lines = [f"Group: {self.name}"]
        for entry in self._entries:
            lines.append(f"  {entry}")
        return "\n".join(lines)


class GroupRegistry:
    def __init__(self) -> None:
        self._groups: Dict[str, CronGroup] = {}

    def create(self, name: str) -> CronGroup:
        name = name.strip()
        if not name:
            raise ValueError("Group name must not be empty.")
        if name in self._groups:
            raise ValueError(f"Group '{name}' already exists.")
        group = CronGroup(name=name)
        self._groups[name] = group
        return group

    def get(self, name: str) -> Optional[CronGroup]:
        return self._groups.get(name)

    def delete(self, name: str) -> bool:
        if name in self._groups:
            del self._groups[name]
            return True
        return False

    def all(self) -> List[CronGroup]:
        return list(self._groups.values())

    def names(self) -> List[str]:
        return list(self._groups.keys())
