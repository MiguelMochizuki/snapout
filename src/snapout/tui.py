"""Interactive curses checklist to choose which revisions to remove."""

from __future__ import annotations

import curses
import os
import sys
from dataclasses import dataclass, field

from .models import Revision
from .render import format_size


@dataclass
class Checklist:
    """Selection state, kept free of curses so it can be tested."""

    items: list[Revision]
    cursor: int = 0
    checked: set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.checked = set(range(len(self.items)))  # everything selected by default

    def move(self, delta: int) -> None:
        self.cursor = max(0, min(len(self.items) - 1, self.cursor + delta))

    def toggle(self) -> None:
        self.checked ^= {self.cursor}

    def toggle_all(self) -> None:
        all_items = set(range(len(self.items)))
        self.checked = set() if self.checked == all_items else all_items

    def selected(self) -> list[Revision]:
        return [r for i, r in enumerate(self.items) if i in self.checked]

    def total_size(self) -> int:
        return sum(r.size for r in self.selected())


def _draw(screen: curses.window, state: Checklist, top: int) -> int:
    """Draw the list and return the (possibly scrolled) top row index."""
    height, width = screen.getmaxyx()
    visible = max(1, height - 3)
    top = min(top, state.cursor)
    top = max(top, state.cursor - visible + 1)

    screen.erase()
    screen.addnstr(0, 0, "Select old revisions to remove", width - 1, curses.A_BOLD)
    for row, i in enumerate(range(top, min(len(state.items), top + visible)), start=1):
        r = state.items[i]
        first_of_name = i == 0 or state.items[i - 1].name != r.name
        mark = "x" if i in state.checked else " "
        name = r.name if first_of_name else ""
        line = f"[{mark}] {name:<24} rev {r.revision:<8} {format_size(r.size):>10}"
        screen.addnstr(row, 0, line, width - 1, curses.A_REVERSE if i == state.cursor else 0)
    status = f"{len(state.checked)}/{len(state.items)} selected, {format_size(state.total_size())}"
    screen.addnstr(
        height - 1,
        0,
        f"{status}  |  space toggle  a all  enter confirm  q quit",
        width - 1,
        curses.A_DIM,
    )
    screen.refresh()
    return top


def _loop(screen: curses.window, state: Checklist) -> list[Revision]:
    curses.curs_set(0)
    top = 0
    while True:
        top = _draw(screen, state, top)
        key = screen.getch()
        if key in (curses.KEY_UP, ord("k")):
            state.move(-1)
        elif key in (curses.KEY_DOWN, ord("j")):
            state.move(1)
        elif key == curses.KEY_PPAGE:
            state.move(-10)
        elif key == curses.KEY_NPAGE:
            state.move(10)
        elif key == ord(" "):
            state.toggle()
        elif key == ord("a"):
            state.toggle_all()
        elif key in (curses.KEY_ENTER, 10, 13):
            return state.selected()
        elif key in (ord("q"), 27):
            return []


def select_revisions(revs: list[Revision]) -> list[Revision] | None:
    """Show the checklist and return the user's choice.

    Args:
        revs: Candidate revisions; all start selected.

    Returns:
        The chosen revisions, [] if the user quit, or None when there is no
        usable terminal.
    """
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None
    os.environ.setdefault("ESCDELAY", "25")
    try:
        return curses.wrapper(_loop, Checklist(revs))
    except curses.error:
        return None
