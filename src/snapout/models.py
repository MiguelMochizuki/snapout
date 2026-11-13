"""Data types shared across SnapOut modules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Revision:
    """One installed revision of a snap, as listed by `snap list --all`."""

    name: str
    version: str
    revision: str
    notes: str
    size: int = 0  # bytes on disk; only filled for old revisions

    @property
    def is_old(self) -> bool:
        """True when `notes` (comma-separated, e.g. "base,disabled") has "disabled"."""
        return "disabled" in self.notes.split(",")
