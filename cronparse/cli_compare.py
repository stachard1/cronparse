"""CLI entry point for cron expression comparison."""

from __future__ import annotations

import argparse
import json
import sys

from cronparse.compare import compare


def build_compare_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronparse-compare",
        description="Compare two cron expressions side by side.",
    )
    parser.add_argument("left", help="First cron expression")
    parser.add_argument("right", help="Second cron expression")
    parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )
    return parser


def _run_compare(args) -> int:
    result = compare(args.left, args.right)

    if not result.left_valid:
        print(f"Error: left expression is invalid: {args.left}", file=sys.stderr)
        return 1
    if not result.right_valid:
        print(f"Error: right expression is invalid: {args.right}", file=sys.stderr)
        return 1

    if args.json:
        data = {
            "left": result.left_expr,
            "right": result.right_expr,
            "identical": result.identical,
            "left_human": result.left_human,
            "right_human": result.right_human,
            "fields": [
                {
                    "field": fc.field_name,
                    "left": fc.left,
                    "right": fc.right,
                    "match": fc.match,
                }
                for fc in result.fields
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(str(result))

    return 0 if result.identical else 2


def main() -> None:  # pragma: no cover
    parser = build_compare_parser()
    args = parser.parse_args()
    sys.exit(_run_compare(args))
