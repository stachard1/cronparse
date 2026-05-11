"""CLI sub-command for managing cron expression groups."""
from __future__ import annotations

import argparse
import sys

from cronparse.group import GroupRegistry
from cronparse.group_export import to_json


def build_group_parser(parent: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = parent.add_parser("group", help="Manage named groups of cron expressions")
    sub = p.add_subparsers(dest="group_cmd", required=True)

    cr = sub.add_parser("create", help="Create a new group")
    cr.add_argument("name", help="Group name")

    ad = sub.add_parser("add", help="Add an expression to a group")
    ad.add_argument("name", help="Group name")
    ad.add_argument("expression", help="Cron expression")
    ad.add_argument("--label", default=None, help="Optional label")

    ls = sub.add_parser("list", help="List groups or entries in a group")
    ls.add_argument("name", nargs="?", default=None, help="Group name (omit for all)")

    ex = sub.add_parser("export", help="Export all groups as JSON")
    _ = ex  # no extra args needed


def _run_group(args: argparse.Namespace, registry: GroupRegistry) -> int:
    cmd = args.group_cmd

    if cmd == "create":
        try:
            registry.create(args.name)
            print(f"Group '{args.name}' created.")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    elif cmd == "add":
        group = registry.get(args.name)
        if group is None:
            print(f"Error: group '{args.name}' not found.", file=sys.stderr)
            return 1
        try:
            entry = group.add(args.expression, label=args.label)
            print(f"Added: {entry}")
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    elif cmd == "list":
        if args.name:
            group = registry.get(args.name)
            if group is None:
                print(f"Error: group '{args.name}' not found.", file=sys.stderr)
                return 1
            print(str(group))
        else:
            groups = registry.all()
            if not groups:
                print("No groups defined.")
            for g in groups:
                print(f"{g.name} ({len(g)} entries)")

    elif cmd == "export":
        print(to_json(registry))

    return 0


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="cronparse-group")
    subs = parser.add_subparsers(dest="group_cmd", required=True)
    build_group_parser(subs)
    args = parser.parse_args()
    registry = GroupRegistry()
    sys.exit(_run_group(args, registry))
