# Changelog

Notable changes to DataCleanr, the web and the desktop version together. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/). The web version is published on every change to `main`; desktop releases are tagged `v<version>` and published on [Releases](https://github.com/RaulEstevezA/DataCleanr/releases).

## [Unreleased]

## [0.1.2] - 2026-10-28

### Added

- Web: the interface opens in the language chosen on the portfolio, and a language chosen here is shared with it.
- Desktop: "Developed by Raúl Estévez" at the bottom, linking to the portfolio, as in the web version.

### Fixed

- Web: the text fields and selectors of the transform panel, the custom value when unifying similar values and the profile name in the history show the focus outline again, so they can be followed with the keyboard.

## [0.1.1] - 2026-10-27

### Added

- Desktop: Windows and Linux builds for ARM64.
- Web: the desktop download button offers the file for the visitor's system, including Windows and Linux on ARM64, with a note on the systems where the app has been tested (macOS, Windows x64 and Linux ARM64).

## [0.1.0] - 2026-10-26

First release: the web version and the desktop version for Windows, macOS and Linux.

### Added

- Import of CSV (delimiter and encoding detected: UTF-8, UTF-16, Windows-1252), Excel `.xlsx` with a sheet selector, JSON tables (lists of objects or of lists, nested fields as `contact.email`, numbers kept exactly as written) and XML tables (row element detected automatically, attributes as `@id`, nested elements as `address.city`; entity declarations rejected).
- A paginated data table with column selection.
- Column cleaning, always shown first as `original → proposed` and accepted or rejected row by row:
  - Trim spaces, collapse repeated spaces, lowercase, UPPERCASE and Title Case.
  - Custom replace, with suggestions from the column values.
  - Phone numbers to E.164, international or national format, choosing the country.
  - Dates to a single format, choosing the input order and how to read two-digit years.
  - Amounts, converting on their own only the unambiguous cases and warning about mixed currencies.
  - Unify similar values: groups different spellings of the same value and the user picks or types the final one, with clean variants suggested.
- Rows: exact duplicates (every column or only the selected ones), possible duplicates scored by similarity and confirmed group by group, and combining duplicates by filling the empty cells of the kept row without overwriting anything.
- Undo and redo of every step (also with `Ctrl/Cmd+Z`) and a history to jump back to any point.
- Cleaning profiles: the history is saved as a JSON file and can be applied to another file, showing the number of changes of each step first. A profile saved in one version works in the other.
- Export to CSV in UTF-8, choosing the delimiter, or to Excel with a type for each column (text, number, date or boolean); values that would lose information (`007`, dates before 1900) are kept as text. Complete and incomplete rows can be exported separately, as two CSVs or two Excel sheets. The original data is kept until export.
- English and Spanish interface. The data is processed locally and never sent to a server.
- Web: portfolio-style navigation and intro card, and buttons to the desktop download and the other tools.
- Desktop: the same behavior as the web version, checked against the same shared test cases (`shared/`), with files imported in the background, drag and drop anywhere in the window and save dialogs that start in the Downloads folder. Packaged with PyInstaller and released by GitHub Actions with an automatic start-up check.

[Unreleased]: https://github.com/RaulEstevezA/DataCleanr/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/RaulEstevezA/DataCleanr/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/RaulEstevezA/DataCleanr/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/RaulEstevezA/DataCleanr/releases/tag/v0.1.0
