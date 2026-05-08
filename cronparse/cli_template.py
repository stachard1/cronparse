"""CLI entry-point for browsing and searching cron templates."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from cronparse.template import Template, TemplateRegistry


def build_template_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronparse-template",
        description="Browse and search built-in cron expression templates.",
    )
    p.add_argument("--tag",    metavar="TAG",   help="Filter templates by tag")
    p.add_argument("--search", metavar="QUERY", help="Search templates by name or description")
    p.add_argument("--name",   metavar="NAME",  help="Show a single template by name")
    p.add_argument("--json",   action="store_true", help="Output as JSON")
    return p


def _template_to_dict(t: Template) -> dict:
    return {
        "name": t.name,
        "expression": t.expression,
        "description": t.description,
        "tags": t.tags,
    }


def _print_templates(templates: List[Template], as_json: bool) -> None:
    if as_json:
        print(json.dumps([_template_to_dict(t) for t in templates], indent=2))
    else:
        for t in templates:
            tags_str = ", ".join(t.tags) if t.tags else ""
            tag_part = f"  [{tags_str}]" if tags_str else ""
            print(f"{t.name:<20}  {t.expression:<16}  {t.description}{tag_part}")


def _run_template(args: argparse.Namespace) -> int:
    registry = TemplateRegistry()

    if args.name:
        t = registry.get(args.name)
        if t is None:
            print(f"Template '{args.name}' not found.", file=sys.stderr)
            return 1
        _print_templates([t], args.json)
        return 0

    if args.tag:
        results = registry.by_tag(args.tag)
        if not results:
            print(f"No templates found for tag '{args.tag}'.", file=sys.stderr)
            return 1
        _print_templates(results, args.json)
        return 0

    if args.search:
        results = registry.search(args.search)
        if not results:
            print(f"No templates matched '{args.search}'.", file=sys.stderr)
            return 1
        _print_templates(results, args.json)
        return 0

    # Default: list all
    _print_templates(registry.all(), args.json)
    return 0


def main() -> None:  # pragma: no cover
    parser = build_template_parser()
    args = parser.parse_args()
    sys.exit(_run_template(args))
