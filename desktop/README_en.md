# DataCleanr · Desktop

Desktop version of DataCleanr: Python + PySide6 + OpenPyXL + RapidFuzz.

It does the same as the web version, without the browser's size limits: it passes the same test cases in [`shared/test-cases/`](../shared/README.md) and reads the same cleaning profiles.

What the tool does and its philosophy are described in the [main README](../README_en.md).

## Download

| System | File |
|---|---|
| macOS (Apple Silicon) | [DataCleanr-macOS.dmg](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-macOS.dmg) |
| Windows | [DataCleanr-Windows.zip](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Windows.zip) |
| Linux | [DataCleanr-Linux.tar.gz](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Linux.tar.gz) |

Every version is in [Releases](https://github.com/RaulEstevezA/DataCleanr/releases).

> [!NOTE]
> Only tested on **macOS**. The Windows and Linux versions are built and pass the tests and an automatic startup check, but nobody has used them on a real computer yet. If you find a problem, write to [contact.raulesteveza@gmail.com](mailto:contact.raulesteveza@gmail.com).

- **macOS:** open the `.dmg` and drag DataCleanr to Applications.
- **Windows:** unzip the `.zip` and run `DataCleanr.exe` inside the `DataCleanr` folder.
- **Linux:** extract with `tar -xzf DataCleanr-Linux.tar.gz` and run `DataCleanr/DataCleanr`. Some distributions need `libxcb-cursor0` installed.

### Opening it the first time

The app is not signed (signing requires paid Apple and Microsoft accounts), so the system shows a warning the first time it is opened:

- **macOS** says it could not verify that the app is free of malware. Click **Done**, go to **System Settings → Privacy & Security**, scroll down to **Security** and click **Open Anyway**. This is only needed once.
- **Windows** shows "Windows protected your PC". Click **More info** and then **Run anyway**.

The code is the one in this repository, and the files are built by GitHub Actions ([workflow](../.github/workflows/release-desktop.yml)).

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

## Build the executable

```bash
pip install -e ".[build]"
pyinstaller packaging/datacleanr.spec
```

The result goes to `dist/`: `DataCleanr.app` on macOS, and a `DataCleanr` folder with the executable on Windows and Linux. PyInstaller does not cross-compile: each one is built on its own operating system.

## Structure

```
datacleanr/
  core/          Logic without UI: each module mirrors one in web/src/core/
  io/            Reading and writing CSV, Excel, JSON and XML
  ui/            PySide6 interface
packaging/       PyInstaller configuration and application icons
tests/           pytest tests, reading the cases in shared/test-cases/
pyproject.toml   Dependencies and configuration
```

[Back to main README](../README_en.md)
