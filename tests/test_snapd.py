from snapout.models import Revision
from snapout.snapd import parse_snap_list

SAMPLE = """\
Name     Version  Rev   Tracking       Publisher  Notes
core22   20240111 1033  latest/stable  canonical✓ base
firefox  130.0    4793  latest/stable  mozilla✓   disabled
firefox  131.0    4848  latest/stable  mozilla✓   -
"""


def test_parse_skips_header_and_reads_columns():
    rows = parse_snap_list(SAMPLE)
    assert rows[0] == Revision("core22", "20240111", "1033", "base")
    assert [r.revision for r in rows] == ["1033", "4793", "4848"]


def test_parse_marks_disabled_in_notes():
    assert [r.notes for r in parse_snap_list(SAMPLE)] == ["base", "disabled", "-"]


def test_parse_ignores_blank_and_short_lines():
    assert parse_snap_list("Name Version Rev\n\nfoo bar\n") == []


def test_disabled_is_detected_among_comma_separated_notes():
    rows = parse_snap_list(
        "Name Version Rev Tracking Publisher Notes\ncore22 1 2 x y base,disabled\n"
    )
    assert rows[0].is_old
    assert not Revision("core22", "1", "3", "base").is_old
