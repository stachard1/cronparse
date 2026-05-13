"""Cron job dependency tracking — define ordering constraints between jobs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from cronparse.exceptions import CronParseError
from cronparse.validator import validate


@dataclass
class DependencyEntry:
    name: str
    expression: str
    depends_on: List[str] = field(default_factory=list)
    description: str = ""

    def __str__(self) -> str:
        deps = ", ".join(self.depends_on) if self.depends_on else "none"
        return f"{self.name} ({self.expression}) -> depends on: [{deps}]"


class DependencyGraph:
    """Registry of named cron jobs with dependency edges."""

    def __init__(self) -> None:
        self._entries: Dict[str, DependencyEntry] = {}

    def add(self, name: str, expression: str, depends_on: Optional[List[str]] = None, description: str = "") -> DependencyEntry:
        name = name.strip()
        if not name:
            raise ValueError("Job name must not be empty.")
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression '{expression}': {result.reason}")
        if name in self._entries:
            raise ValueError(f"Job '{name}' already registered.")
        entry = DependencyEntry(
            name=name,
            expression=expression,
            depends_on=list(depends_on or []),
            description=description.strip(),
        )
        self._entries[name] = entry
        return entry

    def remove(self, name: str) -> None:
        self._entries.pop(name, None)

    def get(self, name: str) -> Optional[DependencyEntry]:
        return self._entries.get(name)

    def all(self) -> List[DependencyEntry]:
        return list(self._entries.values())

    def dependencies_of(self, name: str) -> List[DependencyEntry]:
        entry = self._entries.get(name)
        if entry is None:
            return []
        return [self._entries[d] for d in entry.depends_on if d in self._entries]

    def dependents_of(self, name: str) -> List[DependencyEntry]:
        return [e for e in self._entries.values() if name in e.depends_on]

    def has_cycle(self) -> bool:
        """Return True if the dependency graph contains a cycle."""
        visited: Set[str] = set()
        in_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            in_stack.add(node)
            entry = self._entries.get(node)
            for dep in (entry.depends_on if entry else []):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in in_stack:
                    return True
            in_stack.discard(node)
            return False

        for name in self._entries:
            if name not in visited:
                if dfs(name):
                    return True
        return False

    def topological_order(self) -> List[str]:
        """Return job names in topological order (dependencies first)."""
        if self.has_cycle():
            raise ValueError("Cannot produce topological order: cycle detected.")
        visited: Set[str] = set()
        order: List[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            entry = self._entries.get(node)
            for dep in (entry.depends_on if entry else []):
                if dep not in visited:
                    dfs(dep)
            order.append(node)

        for name in self._entries:
            if name not in visited:
                dfs(name)
        return order
