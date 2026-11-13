"""Argument parsing for the `snapout` command."""

from __future__ import annotations

import argparse


def _add_common(parser: argparse.ArgumentParser, *, root: bool, dry_run: bool = True) -> None:
    # Subparsers use SUPPRESS so they do not overwrite flags given before the subcommand.
    default = False if root else argparse.SUPPRESS
    if dry_run:
        parser.add_argument(
            "-n",
            "--dry-run",
            action="store_true",
            default=default,
            help="show the commands without running them",
        )
    parser.add_argument(
        "--no-color", action="store_true", default=default, help="disable ANSI colors"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the `snapout` parser with its `list` and `clean` subcommands."""
    parser = argparse.ArgumentParser(
        prog="snapout",
        description="Clean up old Snap revisions. Without a command, pick revisions interactively.",
    )
    _add_common(parser, root=True)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    ls = sub.add_parser("list", help="show snaps (old revisions by default)")
    _add_common(ls, root=False, dry_run=False)
    scope = ls.add_mutually_exclusive_group()
    for name in ("old", "active", "all"):
        scope.add_argument(f"--{name}", dest="scope", action="store_const", const=name)
    ls.set_defaults(scope="old")

    clean = sub.add_parser("clean", help="remove old revisions")
    _add_common(clean, root=False)
    clean.add_argument("--select", action="store_true", help="choose which revisions to remove")
    clean.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation")
    return parser
