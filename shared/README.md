# Shared

Language-neutral resources used by both the web (TypeScript) and desktop (Python) versions.

## test-cases/

JSON test cases that define the expected behavior of every feature available in both versions. The Vitest suite (`web/`) and the pytest suite (`desktop/`) load the same files, so if one implementation behaves differently, its tests fail.

`test-cases/files/` holds sample input files (e.g. `sample.xlsx`, generated with OpenPyXL) used by those cases.

When adding a feature that exists in both versions, add its cases here first. Features exclusive to one version keep their tests in that version only.

## How it maps to each version

Shared logic lives in a `core/` folder in each version, with no UI dependencies:

- Web: `web/src/core/` (TypeScript)
- Desktop: `desktop/datacleanr/core/` (Python, planned)

A file in one `core/` has its counterpart in the other (e.g. `transforms.ts` / `transforms.py`), and both must pass the cases in `test-cases/`.

## Notes for the desktop version

- XML: parse with `defusedxml`, not the standard `xml.etree`, which is vulnerable to malicious files (entity expansion). Use the local name of tags and attributes (no namespace), as the web version does.
- JSON: parse numbers as text (`parse_int=str, parse_float=str`) so they are kept exactly as written.
