"""CLI entry-point: cronparse-audit — view and export the audit log."""
from __future__ import annotations

import argparse
import sys

from cronparse.audit import AuditLog
from cronparse.audit_export import to_json, to_text


def build_audit_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronparse-audit",
        description="Display or export the cronparse audit log.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output audit log as JSON.",
    )
    p.add_argument(
        "--action",
        metavar="ACTION",
        help="Filter events by action (e.g. added, removed, validated).",
    )
    return p


def _run_audit(args: argparse.Namespace, log: AuditLog) -> int:
    """Core logic; accepts an :class:`AuditLog` so it is easily testable."""
    filtered = AuditLog()
    events = log.filter_by_action(args.action) if args.action else log.events()
    for e in events:
        filtered._events.append(e)  # noqa: SLF001

    if args.json:
        print(to_json(filtered))
    else:
        print(to_text(filtered))

    return 0


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = build_audit_parser()
    args = parser.parse_args(argv)
    log = AuditLog()  # real usage would load a persisted log
    sys.exit(_run_audit(args, log))
