# DataCleanr

Tool for cleaning, normalizing and deduplicating CSV, Excel, JSON and XML data **without sending files to any server**.

**Try it online:** [raulesteveza.github.io/tools/DataCleanr](https://raulesteveza.github.io/tools/DataCleanr/)

**Download for desktop:** [macOS](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-macOS.dmg) · Windows ([x64](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Windows.zip), [ARM64](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Windows-ARM64.zip)) · Linux ([x64](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Linux.tar.gz), [ARM64](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Linux-ARM64.tar.gz)) ([how to open it](./desktop/README_en.md#opening-it-the-first-time))

<p align="center">
  <a href="https://raulesteveza.github.io/tools/DataCleanr/">
    <img src="docs/images/web_app.png" alt="DataCleanr web version unifying different spellings of the same name" width="720">
  </a>
</p>

## What it is for

Data coming from spreadsheets, forms or exports from other systems is often messy: extra spaces, mixed case, phone numbers and dates written in many ways, repeated rows, and values that mean the same thing but are written differently:

```text
Raúl Estévez
RAUL ESTEVEZ
raul estévez
Estévez, Raúl
```

DataCleanr helps detect and fix these problems before loading the data into a database or another system.

## Philosophy

- **Nothing changes without the user seeing it.** Every transformation first shows an `original value → proposed value` preview, and each change can be accepted or rejected row by row.
- **Doubtful values are not guessed.** If a value is ambiguous (`03/04/2024`, `1.234`) or cannot be converted without losing information (`007`, a phone number with an extension), it is left as is and flagged for manual review.
- **The original is preserved** until export, and everything can be undone.
- **Data never leaves the device.** There is no server: all processing happens locally.

## What it does

### Import

| Format | Details |
|---|---|
| **CSV** | Detects the delimiter (`,` `;` tab) and the encoding (UTF-8, UTF-16, Windows-1252 from Excel in Western locales) |
| **Excel (.xlsx)** | Sheet selector. Dates, numbers and booleans become unambiguous text |
| **JSON** | Lists of objects or of lists, nested objects (`contact.email`). Numbers are kept exactly |
| **XML** | Detects which element is each row. Attributes as `@id`, nested elements as `address.city` |

### Clean a column

| Transformation | Example |
|---|---|
| Trim spaces | `"  Raúl Estévez "` → `"Raúl Estévez"` |
| Collapse repeated spaces | `"laura   NAVARRO"` → `"laura NAVARRO"` |
| lowercase, UPPERCASE, Title Case | `"jean-luc PÉREZ"` → `"Jean-Luc Pérez"` |
| Custom replace | `"Estévez, Raúl"` → `"Raúl Estévez"`, with suggestions from the column values |
| Normalize phone numbers | `"600 123 456"` → `"+34600123456"` (E.164, international or national) |
| Normalize dates | `"13/07/2024"` → `"2024-07-13"`, choosing the input order and how to read two-digit years |
| Normalize amounts | `"4.072,67"`, `"12063.99 €"` → `"4072.67"`, detecting on its own only the unambiguous cases |
| Unify similar values | Groups `Raúl Estévez`, `RAUL ESTEVEZ`, `raul estévez`… and the user picks or types the final value |

### Rows

- **Exact duplicates**, comparing every column or only the selected ones.
- **Possible duplicates**: nearly identical rows (`Juan Pérez` / `juan perez` / `Juan Peres`), scored by similarity. The user confirms each group.
- **Combine rows**: when removing duplicates, the kept row is completed with the data it was missing from the removed ones, without overwriting anything.

### History and profiles

- **Undo and redo** any step (also with `Ctrl/Cmd+Z`) and jump back to any point in the history.
- **Cleaning profiles**: the steps are saved as a JSON file and can be applied to another file, such as next month's. Before applying, the number of changes of each step is shown.

### Export

- **CSV** in UTF-8, choosing the delimiter.
- **Excel (.xlsx)**, choosing for each column whether it is saved as text, number, date or boolean. Values that cannot be converted without losing information (`007`, `1234,56`) are saved as text.

## Versions

| | Web | Desktop |
|---|---|---|
| Technology | React + TypeScript + Vite | Python + PySide6 + OpenPyXL + RapidFuzz |
| Runs in | The browser | Installable application (Windows, macOS, Linux) |
| Status | Published: [raulesteveza.github.io/tools/DataCleanr](https://raulesteveza.github.io/tools/DataCleanr/) | [Download](./desktop/README_en.md#download) (tested on macOS, Windows x64 and Linux ARM64) |
| Documentation | [web/README_en.md](./web/README_en.md) | [desktop/README_en.md](./desktop/README_en.md) |

## Shared behavior

The two versions are written separately (TypeScript and Python), but **they behave the same**: the [`shared/`](./shared/README.md) folder contains JSON test cases (and sample files) that define what each feature must do. The web and desktop tests read the same files, so if one version behaves differently, its tests fail.

The cleaning profile format is shared too: a profile saved in the web version can be used in the desktop version and vice versa.

## Repository structure

```
web/                 Web version (React + TypeScript + Vite)
  src/core/          Logic without UI: transformations, normalization, duplicates, profiles...
  src/components/    React interface
desktop/             Desktop version (Python + PySide6)
shared/              Behavior common to both versions
  test-cases/        JSON test cases and sample files
docs/                Images
```

## Suggestions

Ideas for improvements, bugs or a format you would like DataCleanr to support: write to [contact.raulesteveza@gmail.com](mailto:contact.raulesteveza@gmail.com).

## Developer

**Raul Estevez**

- [Personal Website](https://raulesteveza.github.io/)
- [LinkedIn Profile](https://www.linkedin.com/in/raulesteveza/)

## License

[MIT](./LICENSE)

[Back to main README](./README.md)
