"""Render a CronScheduler summary as a formatted text table."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cronparse.scheduler import CronScheduler

_COL_SEP = "  "
_HEADER = ["NAME", "EXPRESSION", "DESCRIPTION", "NEXT RUN"]


def _col_widths(rows: list[list[str]]) -> list[int]:
    widths = [len(h) for h in _HEADER]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    return widths


def render_table(scheduler: "CronScheduler") -> str:
    """Return a plain-text table of all scheduled jobs."""
    data_rows: list[list[str]] = []
    for job in scheduler:
        runs = job.next_runs(1)
        next_run_str = runs[0] if runs else "—"
        data_rows.append([job.name, job.expression, job.description, next_run_str])

    widths = _col_widths(data_rows)

    def fmt_row(cells: list[str]) -> str:
        return _COL_SEP.join(c.ljust(w) for c, w in zip(cells, widths))

    separator = "-" * (sum(widths) + len(_COL_SEP) * (len(widths) - 1))
    lines: list[str] = [
        fmt_row(_HEADER),
        separator,
    ]
    for row in data_rows:
        lines.append(fmt_row(row))

    if not data_rows:
        lines.append("(no jobs scheduled)")

    return "\n".join(lines)


def render_json(scheduler: "CronScheduler") -> str:
    """Return a JSON string of the scheduler summary."""
    import json

    return json.dumps(scheduler.summary(), indent=2)
