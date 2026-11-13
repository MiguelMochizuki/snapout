"""Plain-text output helpers: sizes, tables and ANSI styling."""

from __future__ import annotations

import os
import sys


def format_size(size_bytes: int) -> str:
    """Format bytes as a human readable size.

    Args:
        size_bytes: Size in bytes.

    Returns:
        A string such as "3.0 KB".
    """
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def color_enabled(no_color: bool = False) -> bool:
    """Tell whether ANSI colors should be used.

    Args:
        no_color: True when the user passed `--no-color`.

    Returns:
        True only on a TTY, unless `NO_COLOR` is set or `TERM=dumb`.
    """
    if no_color or "NO_COLOR" in os.environ or os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


class Style:
    """Wrap text in ANSI codes, or return it unchanged when colors are off."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def bold(self, text: str) -> str:
        return self._wrap("1", text)

    def green(self, text: str) -> str:
        return self._wrap("32", text)

    def red(self, text: str) -> str:
        return self._wrap("31", text)


def table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Format rows as left-aligned columns separated by two spaces.

    Args:
        headers: Column titles, one per column.
        rows: Table rows; each row has as many cells as there are headers.

    Returns:
        The header line followed by one line per row.
    """
    widths = [max(len(cell) for cell in col) for col in zip(headers, *rows, strict=True)]
    return [
        "  ".join(c.ljust(w) for c, w in zip(line, widths, strict=True)).rstrip()
        for line in (headers, *rows)
    ]
