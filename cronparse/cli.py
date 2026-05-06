"""Command-line interface for cronparse."""

import argparse
import json
import sys
from datetime import datetime

from cronparse.formatter import summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronparse",
        description="Parse, validate, and preview cron expressions.",
    )
    parser.add_argument("expression", help="Cron expression (quoted), e.g. '*/5 * * * *'")
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of next-run datetimes to show (default: 5)",
    )
    parser.add_argument(
        "--from",
        dest="from_dt",
        metavar="DATETIME",
        help="Start datetime in ISO format, e.g. 2024-01-15T10:00:00",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    from_dt = None
    if args.from_dt:
        try:
            from_dt = datetime.fromisoformat(args.from_dt)
        except ValueError:
            print(f"Error: invalid datetime '{args.from_dt}'. Use ISO format.", file=sys.stderr)
            return 1

    summary = summarize(args.expression, from_dt=from_dt, count=args.count)

    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        print(summary)

    return 0 if summary.is_valid else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
