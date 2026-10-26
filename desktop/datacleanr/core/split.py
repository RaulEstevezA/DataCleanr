"""Split rows into complete and incomplete ones. Mirrors web/src/core/split.ts."""

from dataclasses import replace

from .dataset import Dataset
from .text import js_trim


def split_row_indexes(rows: list[list[str]], required: list[int]) -> tuple[list[int], list[int]]:
    """(complete, incomplete) row indexes in their original order. A row is complete when every
    required column has a value; whitespace-only counts as empty."""
    complete, incomplete = [], []
    for index, row in enumerate(rows):
        (complete if all(js_trim(row[c]) != "" for c in required) else incomplete).append(index)
    return complete, incomplete


def split_by_completeness(dataset: Dataset, required: list[int]) -> tuple[Dataset, Dataset]:
    """(complete, incomplete) datasets, keeping each row's original position (row_ids)."""
    complete, incomplete = split_row_indexes(dataset.rows, required)

    def pick(indexes: list[int]) -> Dataset:
        return replace(dataset, rows=[dataset.rows[i] for i in indexes], row_ids=[dataset.row_ids[i] for i in indexes])

    return pick(complete), pick(incomplete)
