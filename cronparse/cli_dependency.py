"""CLI sub-command: cronparse-dependency — manage job dependency graphs."""
from __future__ import annotations

import argparse
import sys

from cronparse.dependency import DependencyGraph
from cronparse.dependency_export import to_json, to_text


def build_dependency_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronparse-dependency",
        description="Manage cron job dependency graphs.",
    )
    sub = p.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Register a job.")
    add_p.add_argument("name", help="Unique job name.")
    add_p.add_argument("expression", help="Cron expression.")
    add_p.add_argument("--depends-on", nargs="*", default=[], metavar="JOB", help="Names of prerequisite jobs.")
    add_p.add_argument("--description", default="", help="Optional description.")

    sub.add_parser("list", help="List all registered jobs.")
    sub.add_parser("cycle", help="Check for dependency cycles.")
    sub.add_parser("order", help="Print topological execution order.")

    p.add_argument("--json", action="store_true", help="Output as JSON.")
    return p


def _run_dependency(args: argparse.Namespace, graph: DependencyGraph) -> int:
    cmd = args.command
    use_json = getattr(args, "json", False)

    if cmd == "add":
        try:
            entry = graph.add(
                name=args.name,
                expression=args.expression,
                depends_on=args.depends_on,
                description=args.description,
            )
            print(f"Registered: {entry}")
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if cmd == "list":
        if use_json:
            print(to_json(graph))
        else:
            print(to_text(graph))
        return 0

    if cmd == "cycle":
        if graph.has_cycle():
            print("Cycle detected in dependency graph.", file=sys.stderr)
            return 1
        print("No cycles detected.")
        return 0

    if cmd == "order":
        try:
            order = graph.topological_order()
            for name in order:
                print(name)
            return 0
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    print("No command given. Use --help.", file=sys.stderr)
    return 1


def main() -> None:  # pragma: no cover
    parser = build_dependency_parser()
    args = parser.parse_args()
    graph = DependencyGraph()
    sys.exit(_run_dependency(args, graph))
