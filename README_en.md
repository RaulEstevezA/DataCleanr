# DataCleanr

[Back](README.md) · [Español](README_es.md)

Client-side web tool for cleaning, normalizing and deduplicating CSV/Excel data without sending files to a server.

> **Your data is processed locally.** No file is ever sent to a server.

## What does it do?

DataCleanr helps you clean, normalize and unify messy or inconsistent data before loading it into a database or another system:

- Extra whitespace, inconsistent upper/lower case
- Equivalent values written differently (`TRANSGRAU`, `Trans Grau SL`, `Transgrau S.L.`)
- Dates, phone numbers and numbers in different formats
- Empty values, duplicates and possible duplicates

**Philosophy:** nothing is changed without the user seeing it. Every change is shown as `original value → proposed value` and the user decides whether to accept it. Original data is preserved until export.

## Repository structure

```text
DataCleanr/
├── web/       # Web version (React + TypeScript + Vite) — GitHub Pages
├── desktop/   # Desktop version (Python + PySide6 + Pandas)
├── shared/    # Test cases shared by both versions (JSON)
└── docs/      # Documentation and design notes
```

- [Web version](web/README_en.md)
- [Desktop version](desktop/README_en.md)

## Status

Early development. The first release focuses on the web version: CSV import and basic text transformations.

## License

[MIT](LICENSE)
