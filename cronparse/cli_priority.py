"""CLI interface for the priority queue feature."""
from __future__ import annotations

import argparse
import sys

from cronparse.priority import PriorityLevel, PriorityQueue
from cronparse.priority_export import to_json, to_text
from cronparse.exceptions import CronParseError


def build_priority_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronparse-priority",
        description="Manage a prioritised list of cron expressions.",
    )
    parser.add_argument("expressions", nargs="+", help="Cron expressions to add")
    parser.add_argument(
        "--level",
        choices=[l.name.lower() for l in PriorityLevel],
        default="normal",
        help="Priority level (default: normal)",
    )
    parser.add_argument("--label", default="", help="Optional label")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    return parser


def _run_priority(args: argparse.Namespace) -> int:
    queue = PriorityQueue()
    level = PriorityLevel[args.level.upper()]
    for expr in args.expressions:
        try:
            queue.add(expr, level=level, label=args.label)
        except CronParseError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    if args.json:
        print(to_json(queue))
    else:
        print(to_text(queue))
    return 0


def main() -> None:  # pragma: no cover
    parser = build_priority_parser()
    args = parser.parse_args()
    sys.exit(_run_priority(args))
