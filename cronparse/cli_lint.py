"""CLI sub-command: cronparse lint <expression>"""
from __future__ import annotations

import argparse
import json
import sys

from .lint import lint


def build_lint_parser(subparsers) -> None:  # pragma: no cover
    """Register the *lint* sub-command on *subparsers*."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "lint",
        help="Check a cron expression for suspicious patterns.",
    )
    p.add_argument("expression", help="Cron expression to lint (quote it!)")
    p.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit results as JSON.",
    )
    p.set_defaults(func=_run_lint)


def _run_lint(args: argparse.Namespace) -> int:
    result = lint(args.expression)

    if getattr(args, "as_json", False):
        payload = {
            "expression": result.expression,
            "clean": result.clean,
            "warnings": [
                {"field": w.field, "code": w.code, "message": w.message}
                for w in result.warnings
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(str(result))
    return 0 if result.clean else 1


def main(argv=None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog="cronparse-lint",
        description="Lint a cron expression for suspicious patterns.",
    )
    parser.add_argument("expression", help="Cron expression (quote it!)")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    sys.exit(_run_lint(args))
