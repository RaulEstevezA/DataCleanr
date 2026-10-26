# Shared

Language-neutral resources used by both the web (TypeScript) and desktop (Python) versions.

## test-cases/

JSON test cases that define the expected behavior of every feature available in both versions. The Vitest suite (`web/`) and the pytest suite (`desktop/`) load the same files, so if one implementation behaves differently, its tests fail.

When adding a feature that exists in both versions, add its cases here first. Features exclusive to one version keep their tests in that version only.

## How it maps to each version

Shared logic lives in a `core/` folder in each version, with no UI dependencies:

- Web: `web/src/core/` (TypeScript)
- Desktop: `desktop/datacleanr/core/` (Python, planned)

A file in one `core/` has its counterpart in the other (e.g. `transforms.ts` / `transforms.py`), and both must pass the cases in `test-cases/`.
