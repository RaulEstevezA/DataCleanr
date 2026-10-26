"""In-memory table and immutable edits. Mirrors web/src/core/dataset.ts and changes.ts."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Literal

from .text import js_trim

DatasetFormat = Literal["csv", "xlsx", "json", "xml"]


@dataclass(frozen=True)
class Dataset:
    """Rows are kept as lists (not dicts) so column order is preserved and duplicate header names are allowed."""

    file_name: str
    format: DatasetFormat
    # Header names exactly as they appear in the file (may be empty)
    columns: list[str]
    rows: list[list[str]]
    # Position of each row in the imported file (0-based). Stays stable when rows are removed.
    row_ids: list[int]
    # Sheet name for Excel files; None otherwise
    sheet: str | None = None
    # Delimiter detected on import, reused on CSV export (comma for other formats)
    delimiter: str = ","
    # Encoding detected on import. Export is always UTF-8.
    encoding: str = "utf-8"


def column_label(dataset: Dataset, index: int) -> str:
    """Name to display for a column; empty headers get a positional fallback."""
    return js_trim(dataset.columns[index]) or f"#{index + 1}"


def row_number(dataset: Dataset, index: int) -> int:
    """Row number shown to the user: its line in the imported file (1-based, header excluded)."""
    return dataset.row_ids[index] + 1


def count_modified_cells(original: Dataset, current: Dataset) -> int:
    """Cells whose value differs between the original and the current dataset (removed rows not counted)."""
    count = 0
    for row, row_id in zip(current.rows, current.row_ids, strict=True):
        original_row = original.rows[row_id]
        count += sum(1 for cell, before in zip(row, original_row, strict=True) if cell != before)
    return count


def remove_rows(dataset: Dataset, indexes: set[int]) -> Dataset:
    """Returns a new dataset without the rows at the given indexes. The input is never mutated."""
    if not indexes:
        return dataset
    keep = [i for i in range(len(dataset.rows)) if i not in indexes]
    return replace(dataset, rows=[dataset.rows[i] for i in keep], row_ids=[dataset.row_ids[i] for i in keep])


@dataclass(frozen=True)
class CellChange:
    """A proposed edit to one cell: shown to the user as "original -> proposed" before applying."""

    row: int
    original: str
    proposed: str


def preview_column_changes(dataset: Dataset, column: int, transform: Callable[[str], str]) -> list[CellChange]:
    """Runs `transform` over a column and returns only the cells whose value would change."""
    changes = []
    for index, row in enumerate(dataset.rows):
        original = row[column]
        proposed = transform(original)
        if proposed != original:
            changes.append(CellChange(index, original, proposed))
    return changes


def apply_column_changes(dataset: Dataset, column: int, changes: list[CellChange]) -> Dataset:
    """Returns a new dataset with the changes applied. Unchanged rows are shared, not copied."""
    if not changes:
        return dataset
    rows = list(dataset.rows)
    for change in changes:
        updated = list(rows[change.row])
        updated[column] = change.proposed
        rows[change.row] = updated
    return replace(dataset, rows=rows)
