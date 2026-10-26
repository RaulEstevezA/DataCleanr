# DataCleanr · Web

Web version of DataCleanr. All processing happens in the browser: files are never uploaded to any server.

**Try it online:** [raulesteveza.github.io/tools/DataCleanr](https://raulesteveza.github.io/tools/DataCleanr/)

What the tool does and its philosophy are described in the [main README](../README_en.md). This document explains how it is built and how to run it.

## Technologies

| | Used for |
|---|---|
| [React 19](https://react.dev) + [TypeScript](https://www.typescriptlang.org) | Interface and language |
| [Vite](https://vite.dev) | Development server and build |
| [Papa Parse](https://www.papaparse.com) | Reading and writing CSV |
| [read-excel-file](https://www.npmjs.com/package/read-excel-file) / [write-excel-file](https://www.npmjs.com/package/write-excel-file) | Reading and writing Excel (.xlsx) |
| [libphonenumber-js](https://www.npmjs.com/package/libphonenumber-js) | Validating and formatting phone numbers (JS port of Google's library) |
| [Vitest](https://vitest.dev) + [jsdom](https://github.com/jsdom/jsdom) | Tests |
| [oxlint](https://oxc.rs) | Static analysis |

JSON and XML are read with the browser's built-in functions, without libraries.

`xlsx` (SheetJS) is not used for Excel: the version published on npm is outdated and has known vulnerabilities.

## Run locally

Requirements: Node.js 20.19+ or 22.12+.

```bash
cd web
npm install
npm run dev          # development server at http://localhost:5173
npm test             # unit tests (Vitest)
npm run test:watch   # tests in watch mode
npm run lint         # static analysis with oxlint
npm run build        # type-check and build into dist/
npm run preview      # serve the build at http://localhost:4173/tools/DataCleanr/
```

To test with messy data, create a `local-data/` folder anywhere in the repository: it is in `.gitignore`, so its contents are never committed.

## Structure

```
src/
  core/          Logic without UI or React (each module with its test)
    csv.ts, xlsx.ts, json.ts, xml.ts, encoding.ts    Import
    export.ts, xlsxSheet.ts                          Export
    transforms.ts, replace.ts                        Text transformations
    phone.ts, date.ts, amount.ts                     Normalization
    similar.ts                                       Similar values (fuzzy matching)
    duplicates.ts                                    Exact and possible duplicates, combining rows
    changes.ts, dataset.ts                           Change preview and application
    history.ts, operation.ts                         Undo / redo
    profile.ts                                       Cleaning profiles
  components/    React interface (one component per panel, with its CSS)
  i18n/          English and Spanish texts
  hooks/         useStoredState: remembers options in the browser
  utils/         Downloads and lazy loading of the Excel libraries
```

`core/` does not depend on React: it is the part tested with the shared cases and the one mirrored in `desktop/datacleanr/core/`.

## Tests

```bash
npm test
```

Around 300 tests. Most of them read their cases from [`shared/test-cases/`](../shared/README.md), the same ones the desktop version will use. They include real sample files (an `.xlsx` generated with OpenPyXL) and a round-trip test that writes an Excel file and reads it back.

Fuzzy matching similarities are computed like RapidFuzz's `fuzz.ratio`, and the expected values in the cases were obtained with that library.

## Privacy

- No server and no API calls: files are read with browser functions and results are downloaded from memory.
- No analytics or cookies. The only things stored, in the browser's `localStorage`, are preferences: language, phone and date formats, etc.
- Large libraries (phone rules and Excel) are loaded only when used, from the same website.

## Current limits

| | Limit | Reason |
|---|---|---|
| Change preview | 200 visible rows (the rest is applied anyway) | Keep the browser responsive |
| Unify similar values | 3,000 distinct values per column | Comparison grows with the square of the values |
| Possible duplicates | 5,000 rows | Row-to-row comparison |
| Excel | `.xlsx` only (not the old `.xls`) | Same as OpenPyXL in the desktop version |

Larger files are the use case of the desktop version.

[Back to main README](../README_en.md)
