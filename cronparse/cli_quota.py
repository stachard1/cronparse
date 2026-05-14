"""CLI interface for quota management."""
from __future__ import annotations

import argparse
import sys
from typing import List

from cronparse.quota import QuotaStore
from cronparse.quota_export import to_json, to_text


def build_quota_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronparse-quota",
        description="Manage cron job run quotas.",
    )
    parser.add_argument("expression", nargs="+", help="Cron expression(s) to add")
    parser.add_argument(
        "--max-runs", type=int, default=60, help="Maximum runs allowed in window"
    )
    parser.add_argument(
        "--window-hours", type=int, default=1, help="Window size in hours"
    )
    parser.add_argument("--label", default="", help="Optional label")
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    return parser


def _run_quota(args: argparse.Namespace) -> int:
    store = QuotaStore()
    errors: List[str] = []
    for expr in args.expression:
        try:
            store.add(
                expression=expr,
                max_runs=args.max_runs,
                window_hours=args.window_hours,
                label=args.label,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{expr}: {exc}")

    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    if args.json:
        print(to_json(store))
    else:
        print(to_text(store))
    return 0


def main() -> None:  # pragma: no cover
    parser = build_quota_parser()
    args = parser.parse_args()
    sys.exit(_run_quota(args))
