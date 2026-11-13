"""Entrypoint: parse arguments and dispatch to the commands."""

from __future__ import annotations

import shutil
import sys

from .cli import build_parser
from .commands import clean_command, list_command
from .render import Style, color_enabled
from .snapd import Snapd


def main(argv: list[str] | None = None) -> int:
    """Run SnapOut.

    Args:
        argv: Command-line arguments; defaults to `sys.argv[1:]`.

    Returns:
        The process exit code: 0 on success, 1 on failure or missing `snap`.
    """
    args = build_parser().parse_args(argv)
    if shutil.which("snap") is None:
        print("Error: snap command not found", file=sys.stderr)
        return 1

    ops, style = Snapd(), Style(color_enabled(args.no_color))
    if args.command == "list":
        return list_command(ops, style, args.scope)
    return clean_command(
        ops,
        style,
        select=args.command is None or args.select,
        dry_run=args.dry_run,
        yes=getattr(args, "yes", False),
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
