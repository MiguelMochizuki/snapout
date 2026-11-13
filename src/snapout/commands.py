"""Use-cases behind the `list` and `clean` commands."""

from __future__ import annotations

import sys
from typing import Protocol

from . import tui
from .models import Revision
from .render import Style, format_size, table


class SnapOperations(Protocol):
    """What the commands need from the system; `snapd.Snapd` implements it."""

    def all_rows(self) -> list[Revision]: ...

    def remove_revision(self, name: str, revision: str, dry_run: bool) -> int: ...


def _show(revs: list[Revision], style: Style, with_state: bool) -> None:
    headers = ["NAME", "VERSION", "REV", "SIZE"] + (["STATE"] if with_state else [])
    rows = [
        [r.name, r.version, r.revision, format_size(r.size) if r.is_old else "-"]
        + ([("old" if r.is_old else "active")] if with_state else [])
        for r in revs
    ]
    header, *body = table(headers, rows)
    print(style.bold(header))
    print("\n".join(body))


def list_command(ops: SnapOperations, style: Style, scope: str = "old") -> int:
    """Print snaps as a table on stdout and a summary on stderr.

    Args:
        ops: System operations.
        style: Output styling.
        scope: Which revisions to show: "old", "active" or "all".

    Returns:
        The exit code (always 0).
    """
    revs = [r for r in ops.all_rows() if scope == "all" or r.is_old == (scope == "old")]
    if not revs:
        print(
            f"No {scope} snaps found." if scope != "old" else "No old revisions found.",
            file=sys.stderr,
        )
        return 0
    _show(revs, style, with_state=scope == "all")
    old = [r for r in revs if r.is_old]
    reclaimable = format_size(sum(r.size for r in old))
    summary = {
        "old": f"{len(old)} old revisions, {reclaimable} reclaimable",
        "active": f"{len(revs)} active snaps",
        "all": f"{len(revs) - len(old)} active, {len(old)} old revisions "
        f"({reclaimable} reclaimable)",
    }[scope]
    print(summary, file=sys.stderr)  # stderr keeps stdout a clean table for scripts
    return 0


def clean_command(
    ops: SnapOperations, style: Style, *, select: bool, dry_run: bool, yes: bool
) -> int:
    """Remove old revisions, continuing past failures.

    Args:
        ops: System operations.
        style: Output styling.
        select: Let the user choose revisions in the interactive checklist.
        dry_run: Show the commands without running them.
        yes: Skip the confirmation prompt.

    Returns:
        0 on success or when there is nothing to do; 1 if a removal failed,
        confirmation was needed but unavailable, or no terminal was available
        for the checklist.
    """
    old = [r for r in ops.all_rows() if r.is_old]
    if not old:
        print("Nothing to clean.")
        return 0

    chosen = tui.select_revisions(old) if select else old
    if chosen is None:
        print("Interactive selection needs a terminal; use `clean -y` instead.", file=sys.stderr)
        return 1
    if not chosen:
        print("Nothing selected.")
        return 0

    total = sum(r.size for r in chosen)
    if not (yes or dry_run):
        _show(chosen, style, with_state=False)
        try:
            answer = input(f"Remove {len(chosen)} revisions ({format_size(total)})? [y/N] ")
        except EOFError:
            print("\nConfirmation required: rerun with -y/--yes.", file=sys.stderr)
            return 1
        if answer.strip().lower() != "y":
            print("Canceled.")
            return 0

    failed: list[Revision] = []
    freed = 0
    for r in chosen:
        label = f"{r.name} rev {r.revision} ({format_size(r.size)})"
        if ops.remove_revision(r.name, r.revision, dry_run) == 0:
            freed += r.size
            print(f"{style.green('✓')} {label}")
        else:
            failed.append(r)
            print(f"{style.red('✗')} {label}")

    verb = "Would free" if dry_run else "Freed"
    print(f"{len(chosen) - len(failed)}/{len(chosen)} removed. {verb} {format_size(freed)}.")
    if failed:
        names = ", ".join(f"{r.name} rev {r.revision}" for r in failed)
        print(f"Failed: {names}", file=sys.stderr)
        return 1
    return 0
