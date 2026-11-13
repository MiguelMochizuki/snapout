# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.3.0] - 2026-11-13

### Added

- After a real `clean`, SnapOut detaches loop devices still backed by a deleted snap file, which GNOME showed as a stray volume. Loops still mounted by running snap apps stay until those restart.

## [0.2.0] - 2026-11-13

### Changed

- **Breaking:** the nine commands (`scan-*`, `select-*`, `purge-*`) are replaced by `snapout list` and `snapout clean`. There are no aliases.
- SnapOut now only removes old revisions. Removing active packages is no longer supported; use `snap remove`.
- `snapout` with no arguments opens a `curses` checklist instead of the numbered menu.
- `list` prints the table on stdout and the summary on stderr.
- The minimum Python version is now 3.10.
- The `./snapout` bash wrapper was removed; install with `pipx install .` or `pip install .`.

### Added

- `clean -y/--yes` for non-interactive use.
- `pytest` tests, `ruff` and `mypy` configuration, and a GitHub Actions workflow.

### Fixed

- Revisions whose notes are comma-separated (such as `base,disabled` or `snapd,disabled`) are now recognized as old.
- `--no-color` and `-n` work when given before the subcommand.
- A failed removal no longer hides the others: SnapOut continues, reports the failures and exits with status 1.
