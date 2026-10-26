# DataCleanr · Desktop

Desktop version of DataCleanr: Python + PySide6 + Pandas + OpenPyXL + RapidFuzz.

> [!NOTE]
> **In development.** It will be built after the web version, with the same behavior: it will implement the test cases in [`shared/test-cases/`](../shared/README.md) and read the same cleaning profiles.

What the tool does and its philosophy are described in the [main README](../README_en.md).

## Run locally

Requirements: Python 3.11 or later.

```bash
cd desktop
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest                   # tests (shared cases from shared/test-cases/)
ruff check .                       # static analysis
python -m datacleanr               # run the application
```

## Structure

```
datacleanr/
  core/          Logic without UI: each module mirrors one in web/src/core/
tests/           pytest tests, reading the cases in shared/test-cases/
pyproject.toml   Dependencies and configuration
```

[Back to main README](../README_en.md)
