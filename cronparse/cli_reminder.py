"""CLI entry-point for reminder management."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from cronparse.reminder import ReminderStore
from cronparse.reminder_export import to_text

_DATE_FMT = "%Y-%m-%dT%H:%M:%S"


def build_reminder_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronparse-reminder",
        description="Manage cron expression reminders.",
    )
    sub = p.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Add a reminder")
    add_p.add_argument("expression", help="Cron expression")
    add_p.add_argument("message", help="Reminder message")
    add_p.add_argument("due", help=f"Due datetime ({_DATE_FMT})")
    add_p.add_argument("--label", default=None, help="Optional label")

    sub.add_parser("list", help="List all reminders")
    sub.add_parser("overdue", help="List overdue reminders")
    return p


def _run_reminder(args: argparse.Namespace, store: ReminderStore) -> int:
    if args.command == "add":
        try:
            due = datetime.strptime(args.due, _DATE_FMT)
            reminder = store.add(args.expression, args.message, due, args.label)
            print(f"Added: {reminder}")
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if args.command == "list":
        print(to_text(store))
        return 0

    if args.command == "overdue":
        items = store.overdue()
        if not items:
            print("No overdue reminders.")
        else:
            for r in items:
                print(str(r))
        return 0

    print("No command given. Use --help.", file=sys.stderr)
    return 1


def main() -> None:  # pragma: no cover
    parser = build_reminder_parser()
    args = parser.parse_args()
    store = ReminderStore()
    sys.exit(_run_reminder(args, store))
