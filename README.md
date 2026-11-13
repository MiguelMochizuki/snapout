# SnapOut

Command-line tool that removes the old revisions Snap keeps on disk.

## Overview

Snap keeps previous revisions of every package (marked `disabled` in `snap list --all`) so it can roll back. They take space and are never removed automatically. SnapOut lists them with their size and removes them in one step or after you pick which ones.

It only touches old revisions. Active packages are never removed. To uninstall an app, use `snap remove`.

## Quick Start

Requires Linux with `snap` and Python 3.10 or newer. Removals run `sudo snap remove`.

```bash
git clone https://github.com/MiguelMochizuki/snapout.git
cd snapout
pipx install .    # or: pip install .

snapout list              # what can be reclaimed
snapout -n clean -y       # preview the removal (dry run)
snapout clean             # remove all old revisions, asking first
```

## Project Organization

```
snapout/
├── .github/          # GitHub config
│   └── workflows/
│       └── ci.yml
├── src/              # source code
│   └── snapout/      # the package
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── commands.py
│       ├── models.py
│       ├── render.py
│       ├── snapd.py  # only module that calls snap
│       └── tui.py    # curses checklist
├── tests/            # test suite
│   ├── test_commands.py
│   └── test_snapd.py
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
└── README.md
```

### Key modules

- `snapd.py` runs `snap list` and `snap remove`, and parses the output.
- `commands.py` holds the `list` and `clean` logic. It talks to the system through the `SnapOperations` protocol, which the tests replace with a fake.
- `tui.py` is the interactive checklist; `render.py` formats tables, sizes and colors.

## Main Tools & Stack

- **Language:** Python 3.10+, standard library only (no runtime dependencies).
- **Interface:** `argparse` for the CLI and `curses` for the checklist.
- **Development:** `pytest`, `ruff` and `mypy`, installed with `pip install -e ".[dev]"`.
- **CI:** GitHub Actions runs lint, format check, type check and tests on Python 3.10 to 3.13.

## Usage

### List

```bash
snapout list            # old revisions (default)
snapout list --active   # active packages
snapout list --all      # everything, with a STATE column
```

The table goes to stdout and the summary line to stderr, so the output can be piped to `awk` or `grep`.

### Clean

```bash
snapout clean            # remove all old revisions, after confirmation
snapout clean -y         # no confirmation (for scripts)
snapout clean --select   # choose revisions in a checklist
snapout                  # same as `clean --select`
snapout -n clean         # dry run: print the commands, remove nothing
```

In the checklist, every revision starts selected. Use the arrow keys or `j`/`k` to move, `space` to toggle one, `a` to toggle all, `enter` to confirm and `q` to quit.

If a removal fails, SnapOut keeps going, lists the failures at the end and exits with status 1.

### Options

| Option | Applies to | Effect |
|--------|------------|--------|
| `-n`, `--dry-run` | `clean` | Show the commands without running them |
| `-y`, `--yes` | `clean` | Skip the confirmation prompt |
| `--select` | `clean` | Choose which revisions to remove |
| `--old`, `--active`, `--all` | `list` | Pick what to list |
| `--no-color` | all | Disable colors (`NO_COLOR` also works) |

### Tests

```bash
pip install -e ".[dev]"
pytest
```

## Documentation Conventions

Python docstrings follow the Google style. See [CONTRIBUTING.md](CONTRIBUTING.md#documentation-conventions).

## Contributing

Setup, checks and commit style are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
