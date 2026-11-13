"""Argument parsing for the `snapout` command."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version

EPILOG = """\
Exit codes:
  0   success
  1   runtime error (removal failed, snap missing, no terminal)
  2   invalid usage

Examples:
  snapout list
  snapout -n clean
  snapout clean -y
"""


def _version() -> str:
    try:
        return version("snapout")
    except PackageNotFoundError:  # running from a bare checkout
        return "unknown"


class _Formatter(argparse.RawDescriptionHelpFormatter):
    """Capitalized `Usage:` to match the other tools' help layout."""

    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, "Usage: " if prefix is None else prefix)


def _titles(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser._positionals.title = "Commands"  # ponytail: private argparse attrs, no public API
    parser._optionals.title = "Options"
    return parser


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
        "-q", "--quiet", action="store_true", default=default, help="print only errors and data"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=default,
        help="print each command before running it",
    )
    parser.add_argument(
        "--no-color", action="store_true", default=default, help="disable ANSI colors"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the `snapout` parser with its `list` and `clean` subcommands."""
    parser = argparse.ArgumentParser(
        prog="snapout",
        description="Clean up old Snap revisions. Without a command, pick revisions interactively.",
        epilog=EPILOG,
        formatter_class=_Formatter,
    )
    parser.add_argument("-V", "--version", action="version", version=f"snapout {_version()}")
    _titles(parser)
    _add_common(parser, root=True)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    ls = _titles(
        sub.add_parser(
            "list", help="show snaps (old revisions by default)", formatter_class=_Formatter
        )
    )
    _add_common(ls, root=False, dry_run=False)
    scope = ls.add_mutually_exclusive_group()
    for name in ("old", "active", "all"):
        scope.add_argument(f"--{name}", dest="scope", action="store_const", const=name)
    ls.set_defaults(scope="old")

    clean = _titles(
        sub.add_parser("clean", help="remove old revisions", formatter_class=_Formatter)
    )
    _add_common(clean, root=False)
    clean.add_argument("--select", action="store_true", help="choose which revisions to remove")
    clean.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation")
    return parser
