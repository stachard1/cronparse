"""Serialisation helpers for :class:`ForecastWindow`."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .forecast import ForecastWindow

_DT_FMT = "%Y-%m-%dT%H:%M:%S"


def _window_to_dict(fw: ForecastWindow) -> Dict[str, Any]:
    return {
        "expression": fw.expression,
        "start": fw.start.strftime(_DT_FMT),
        "end": fw.end.strftime(_DT_FMT),
        "count": fw.count,
        "runs_per_hour": round(fw.runs_per_hour, 4),
        "run_times": [dt.strftime(_DT_FMT) for dt in fw.run_times],
    }


def to_json(windows: List[ForecastWindow], *, indent: int = 2) -> str:
    """Serialise a list of :class:`ForecastWindow` objects to a JSON string."""
    return json.dumps([_window_to_dict(w) for w in windows], indent=indent)


def to_text(windows: List[ForecastWindow]) -> str:
    """Return a human-readable plain-text summary of forecast windows."""
    if not windows:
        return "No forecast data."

    lines: List[str] = []
    for fw in windows:
        lines.append(f"Expression : {fw.expression}")
        lines.append(f"Window     : {fw.start.strftime(_DT_FMT)} -> {fw.end.strftime(_DT_FMT)}")
        lines.append(f"Runs       : {fw.count}")
        lines.append(f"Rate       : {fw.runs_per_hour:.2f} runs/hour")
        if fw.run_times:
            lines.append("Next runs  :")
            for dt in fw.run_times[:5]:
                lines.append(f"  - {dt.strftime(_DT_FMT)}")
            if fw.count > 5:
                lines.append(f"  ... and {fw.count - 5} more")
        lines.append("")
    return "\n".join(lines).rstrip()
