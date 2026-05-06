"""Command-line interface for cronparse."""

import argparse
import json
import sys

from cronparse.formatter import summarize
from cronparse.differ import diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronparse",
        description="Human-readable cron expression parser and validator.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Default: summarize a single expression
    parser.add_argument(
        "expression",
        nargs="?",
        help="Cron expression to parse (e.g. '*/5 * * * *')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    parser.add_argument(
        "--next",
        type=int,
        default=5,
        metavar="N",
        help="Number of next run timestamps to show (default: 5)",
    )

    # Subcommand: diff two expressions
    diff_parser = subparsers.add_parser(
        "diff",
        help="Compare two cron expressions field by field",
    )
    diff_parser.add_argument("old", help="Original cron expression")
    diff_parser.add_argument("new", help="New cron expression")
    diff_parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "diff":
        try:
            result = diff(args.old, args.new)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

        if args.json:
            output = {
                "old_expression": result.old_expression,
                "new_expression": result.new_expression,
                "has_changes": result.has_changes,
                "changes": [
                    {"field": c.field, "old": c.old_value, "new": c.new_value}
                    for c in result.changes
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print(result.summary())
        sys.exit(0)

    # Default summarize command
    if not args.expression:
        parser.print_help()
        sys.exit(1)

    summary = summarize(args.expression, count=args.next)

    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        print(str(summary))

    sys.exit(0 if summary.is_valid else 1)


if __name__ == "__main__":
    main()
