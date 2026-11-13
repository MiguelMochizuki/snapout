"""System access for SnapOut: the only module that talks to the `snap` binary."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from .models import Revision

SNAP_DIR = Path("/var/lib/snapd/snaps")


def parse_snap_list(output: str) -> list[Revision]:
    """Parse `snap list --all` output.

    Args:
        output: Raw command output; the first line is the header and is skipped.

    Returns:
        One `Revision` per line that has at least name, version and revision.
        `size` is left at 0.
    """
    rows: list[Revision] = []
    for raw_line in output.splitlines()[1:]:
        parts = raw_line.split()
        if len(parts) < 3:
            continue
        rows.append(Revision(parts[0], parts[1], parts[2], parts[-1]))
    return rows


def stale_loops(output: str) -> list[str]:
    """Pick loop devices still backed by a deleted snap file from `losetup -l -n` output."""
    prefix = f"{SNAP_DIR}/"
    return [
        parts[0]
        for line in output.splitlines()
        if len(parts := line.split()) >= 3
        and parts[-1] == "(deleted)"
        and parts[-2].startswith(prefix)
    ]


def _file_size(name: str, revision: str) -> int:
    try:
        return (SNAP_DIR / f"{name}_{revision}.snap").stat().st_size
    except OSError:
        return 0


def _sudo(args: list[str]) -> list[str]:
    return args if os.geteuid() == 0 else ["sudo", *args]


def _run(args: list[str], dry_run: bool, verbose: bool = False) -> int:
    cmd = _sudo(args)
    if dry_run:
        print(f"[DRY RUN] {' '.join(cmd)}")
        return 0
    if verbose:
        print(f"+ {' '.join(cmd)}", file=sys.stderr)
    return subprocess.run(cmd, check=False).returncode


class Snapd:
    """Real implementation of `commands.SnapOperations`."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def all_rows(self) -> list[Revision]:
        """List every installed revision; old ones carry their size on disk."""
        completed = subprocess.run(
            ["snap", "list", "--all", "--color=never"],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return []
        return [
            replace(r, size=_file_size(r.name, r.revision)) if r.is_old else r
            for r in parse_snap_list(completed.stdout)
        ]

    def remove_revision(self, name: str, revision: str, dry_run: bool) -> int:
        """Remove one revision with `snap remove --revision` (through sudo if needed).

        Returns:
            The exit code of the command; 0 in dry-run.
        """
        return _run(["snap", "remove", "--revision", revision, name], dry_run, self.verbose)

    def detach_stale_loops(self) -> int:
        """Detach loop devices left behind by removed snap files; returns how many."""
        out = subprocess.run(
            ["losetup", "-l", "-n", "-O", "NAME,BACK-FILE"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        return sum(_run(["losetup", "-d", d], False, self.verbose) == 0 for d in stale_loops(out))
