# Contributing

Contributions are welcome. Please open a pull request from a feature branch.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

See the README for any project-specific setup (e.g. downloading data or models).

## Tests

```bash
pytest
```

## Workflow

- Branch from `main` and keep each pull request focused on a single change.
- Add or update tests for any behaviour you change.
- Make sure the test suite passes before opening the pull request.
