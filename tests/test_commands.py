import builtins

import pytest

from snapout.cli import build_parser
from snapout.commands import clean_command, list_command
from snapout.models import Revision
from snapout.render import Style
from snapout.tui import Checklist

STYLE = Style(False)
ROWS = [
    Revision("core22", "2024", "1033", "base"),
    Revision("firefox", "130.0", "4793", "disabled", size=2048),
    Revision("firefox", "131.0", "4848", "-"),
    Revision("vlc", "3.0", "100", "disabled", size=1024),
]


class FakeOps:
    def __init__(self, fail: set[str] | None = None) -> None:
        self.removed: list[tuple[str, str, bool]] = []
        self.fail = fail or set()

    def all_rows(self) -> list[Revision]:
        return ROWS

    def remove_revision(self, name: str, revision: str, dry_run: bool) -> int:
        self.removed.append((name, revision, dry_run))
        return 1 if revision in self.fail else 0


def test_list_old_prints_table_on_stdout_and_summary_on_stderr(capsys):
    assert list_command(FakeOps(), STYLE, "old") == 0
    out, err = capsys.readouterr()
    assert out.splitlines()[0].split() == ["NAME", "VERSION", "REV", "SIZE"]
    assert "4793" in out and "4848" not in out
    assert "2 old revisions, 3.0 KB reclaimable" in err


def test_list_all_has_state_column(capsys):
    list_command(FakeOps(), STYLE, "all")
    assert "STATE" in capsys.readouterr().out


def test_clean_yes_removes_all_old(capsys):
    ops = FakeOps()
    assert clean_command(ops, STYLE, select=False, dry_run=False, yes=True) == 0
    assert ops.removed == [("firefox", "4793", False), ("vlc", "100", False)]
    assert "2/2 removed. Freed 3.0 KB." in capsys.readouterr().out


def test_clean_dry_run_skips_prompt_and_passes_flag():
    ops = FakeOps()
    assert clean_command(ops, STYLE, select=False, dry_run=True, yes=False) == 0
    assert all(dry for *_, dry in ops.removed)


def test_clean_declined_removes_nothing(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "n")
    ops = FakeOps()
    assert clean_command(ops, STYLE, select=False, dry_run=False, yes=False) == 0
    assert ops.removed == []


def test_clean_without_tty_requires_yes(monkeypatch):
    def eof(_: str) -> str:
        raise EOFError

    monkeypatch.setattr(builtins, "input", eof)
    assert clean_command(FakeOps(), STYLE, select=False, dry_run=False, yes=False) == 1


def test_clean_continues_after_failure_and_reports(capsys):
    ops = FakeOps(fail={"4793"})
    assert clean_command(ops, STYLE, select=False, dry_run=False, yes=True) == 1
    assert len(ops.removed) == 2
    assert "Failed: firefox rev 4793" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [["-n", "clean"], ["clean", "-n"]])
def test_dry_run_accepted_before_or_after_subcommand(argv):
    assert build_parser().parse_args(argv).dry_run is True


def test_no_color_before_subcommand_is_not_overwritten():
    assert build_parser().parse_args(["--no-color", "list"]).no_color is True


def test_list_scope_default_and_override():
    assert build_parser().parse_args(["list"]).scope == "old"
    assert build_parser().parse_args(["list", "--all"]).scope == "all"


def test_clean_select_without_terminal_fails(monkeypatch, capsys):
    monkeypatch.setattr("snapout.tui.select_revisions", lambda _: None)
    ops = FakeOps()
    assert clean_command(ops, STYLE, select=True, dry_run=False, yes=True) == 1
    assert ops.removed == [] and "needs a terminal" in capsys.readouterr().err


def test_clean_select_removes_only_chosen(monkeypatch):
    monkeypatch.setattr("snapout.tui.select_revisions", lambda revs: revs[1:])
    ops = FakeOps()
    clean_command(ops, STYLE, select=True, dry_run=False, yes=True)
    assert ops.removed == [("vlc", "100", False)]


def test_checklist_starts_all_selected_and_toggles():
    c = Checklist(ROWS[1::2])  # firefox 4793 (2048), vlc (1024)
    assert c.total_size() == 3072
    c.toggle()
    assert [r.name for r in c.selected()] == ["vlc"] and c.total_size() == 1024
    c.toggle_all()
    assert c.selected() == [ROWS[1], ROWS[3]]
    c.toggle_all()
    assert c.selected() == []


def test_checklist_cursor_is_clamped():
    c = Checklist(ROWS)
    c.move(-5)
    assert c.cursor == 0
    c.move(99)
    assert c.cursor == len(ROWS) - 1
