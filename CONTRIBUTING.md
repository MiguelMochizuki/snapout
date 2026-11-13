# Contributing

## Development setup

```bash
git clone https://github.com/MiguelMochizuki/snapout.git
cd snapout
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

Before opening a pull request, run what the CI runs:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

When trying removals by hand, always pass `-n/--dry-run`. Without it SnapOut runs `sudo snap remove` for real.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`, `ci:`).

## Documentation Conventions

### Python

Docstrings use the **Google style**. Type hints carry the types, so the docstring does not repeat them.

- **Module:** a one-line docstring at the top of the file saying what the module is for. Do not repeat the file name.
- **Public function, method or class:** a summary line. Add `Args:`, `Returns:` and `Raises:` only when they say something the signature and the summary do not.
- **Trivial code** (one-line properties, obvious wrappers, tests): no docstring needed.
- Private helpers (`_name`) get a docstring only when the logic is not obvious.

```python
"""Plain-text output helpers: sizes, tables and ANSI styling."""


def table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Format rows as left-aligned columns separated by two spaces.

    Args:
        headers: Column titles, one per column.
        rows: Table rows; each row has as many cells as there are headers.

    Returns:
        The header line followed by one line per row.
    """
```
