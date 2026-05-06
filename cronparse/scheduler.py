"""Cron schedule builder: compose and manage multiple named cron jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional

from cronparse.exceptions import CronParseError
from cronparse.next_run import next_run
from cronparse.parser import CronExpression
from cronparse.validator import validate


@dataclass
class ScheduledJob:
    name: str
    expression: str
    description: str = ""

    def __str__(self) -> str:
        return f"{self.name!r}: {self.expression}"

    def next_runs(self, count: int = 5) -> List[str]:
        """Return the next *count* ISO-formatted run times."""
        expr = CronExpression(self.expression)
        return [dt.isoformat(timespec="seconds") for dt in next_run(expr, count=count)]


class CronScheduler:
    """Container for multiple named cron jobs."""

    def __init__(self) -> None:
        self._jobs: Dict[str, ScheduledJob] = {}

    # ------------------------------------------------------------------
    def add(self, name: str, expression: str, description: str = "") -> ScheduledJob:
        """Add a validated job; raises CronParseError on bad expression."""
        if not name or not name.strip():
            raise ValueError("Job name must not be empty.")
        result = validate(expression)
        if not result.valid:
            raise CronParseError(f"Invalid expression {expression!r}: {result.errors}")
        job = ScheduledJob(name=name.strip(), expression=expression, description=description)
        self._jobs[job.name] = job
        return job

    def remove(self, name: str) -> None:
        """Remove a job by name; raises KeyError if not found."""
        if name not in self._jobs:
            raise KeyError(f"No job named {name!r}.")
        del self._jobs[name]

    def get(self, name: str) -> Optional[ScheduledJob]:
        return self._jobs.get(name)

    def all_jobs(self) -> List[ScheduledJob]:
        return list(self._jobs.values())

    def __len__(self) -> int:
        return len(self._jobs)

    def __iter__(self) -> Iterator[ScheduledJob]:
        return iter(self._jobs.values())

    def summary(self) -> List[Dict]:
        """Return a list of dicts suitable for serialisation."""
        return [
            {
                "name": job.name,
                "expression": job.expression,
                "description": job.description,
                "next_runs": job.next_runs(3),
            }
            for job in self._jobs.values()
        ]
