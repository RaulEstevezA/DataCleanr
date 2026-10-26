"""Exact and possible duplicate rows, and merging them. Mirrors web/src/core/duplicates.ts."""

import math
from dataclasses import dataclass, field

import numpy as np
from rapidfuzz import fuzz, process

from .similar import comparison_key
from .text import collapse_whitespace, js_trim


@dataclass(frozen=True)
class DuplicateOptions:
    # Indexes of the columns to compare
    columns: list[int]
    # Treat "TRANSGRAU " and "transgrau" as equal: lowercase, trim and collapse inner spaces
    ignore_case_and_spaces: bool


def find_duplicate_rows(rows: list[list[str]], options: DuplicateOptions) -> list[list[int]]:
    """Finds rows with the same values in the compared columns.

    Returns groups of row indexes (ascending), ordered by their first row. Rows whose
    compared cells are all empty are ignored: missing data is not a duplicate.
    """
    if not options.columns:
        return []

    def normalize(value: str) -> str:
        return collapse_whitespace(js_trim(value)).lower() if options.ignore_case_and_spaces else value

    groups: dict[tuple[str, ...], list[int]] = {}
    for index, row in enumerate(rows):
        # A tuple compares cell by cell, so "ab" + "c" never equals "a" + "bc"
        key = tuple(normalize(row[column]) for column in options.columns)
        if all(js_trim(cell) == "" for cell in key):
            continue
        groups.setdefault(key, []).append(index)
    # dicts keep insertion order, so groups are already ordered by their first row
    return [group for group in groups.values() if len(group) > 1]


@dataclass(frozen=True)
class SimilarRowsOptions:
    columns: list[int]
    # Minimum average similarity (0-100) for two rows to be possible duplicates
    threshold: float
    ignore_legal_forms: bool


@dataclass
class SimilarRowsGroup:
    # Row indexes, ascending. The first one is the group's reference row.
    rows: list[int]
    # Similarity of each row to the reference row (the reference itself scores 100)
    scores: list[float] = field(default_factory=list)


def find_similar_rows(rows: list[list[str]], options: SimilarRowsOptions) -> list[SimilarRowsGroup]:
    """Finds rows that are probably the same record written differently.

    Greedy, in row order: each row joins the first group whose reference row is at least
    `threshold` similar, otherwise it starts a new group. Only groups with two or more rows
    are returned.

    Row similarity is the average similarity over the compared columns. Columns where either
    cell is empty are skipped, and at least half of the columns must be comparable. Each row
    is scored against every group at once with RapidFuzz's cdist (native code), which keeps
    large files fast; the result is the same as comparing one group at a time.
    """
    if not options.columns:
        return []
    # Comparison keys of the compared columns; blank cells become ''
    keys = [
        [
            "" if js_trim(row[column]) == "" else comparison_key(row[column], options.ignore_legal_forms)
            for column in options.columns
        ]
        for row in rows
    ]
    column_count = len(options.columns)
    min_comparable = math.ceil(column_count / 2)

    groups: list[SimilarRowsGroup] = []
    # Reference row keys of every group, one list per column (same order as `groups`),
    # and whether each of those cells has data (preallocated: at most one group per row)
    leaders: list[list[str]] = [[] for _ in range(column_count)]
    leader_present = np.zeros((column_count, len(rows)), dtype=bool)
    for index, key in enumerate(keys):
        if not any(key):
            continue
        match = None
        if groups:
            total = np.zeros(len(groups))
            comparable = np.zeros(len(groups), dtype=int)
            for c in range(column_count):
                if not key[c]:
                    continue
                present = leader_present[c, : len(groups)]
                scores = process.cdist([key[c]], leaders[c], scorer=fuzz.ratio, dtype=np.float64)[0]
                total += np.where(present, scores, 0.0)
                comparable += present
            with np.errstate(invalid="ignore", divide="ignore"):
                averages = total / comparable
            eligible = (comparable > 0) & (comparable >= min_comparable) & (averages >= options.threshold)
            candidates = np.flatnonzero(eligible)
            if candidates.size:
                match = int(candidates[0])
        if match is None:
            for c in range(column_count):
                leaders[c].append(key[c])
                leader_present[c, len(groups)] = bool(key[c])
            groups.append(SimilarRowsGroup([index], [100.0]))
        else:
            groups[match].rows.append(index)
            groups[match].scores.append(float(averages[match]))
    return [group for group in groups if len(group.rows) > 1]


@dataclass(frozen=True)
class MergedRow:
    row: list[str]
    # Columns of the kept row that were empty and got a value from another row
    filled: list[int]
    # Filled columns where the other rows had different values (the first one was used)
    conflicts: list[int]


def merge_rows(rows: list[list[str]], keep: int) -> MergedRow:
    """Combines a group of duplicate rows into the kept one: its empty cells are filled with
    the first non-empty value found in the other rows (in row order). Values already in the
    kept row are never overwritten."""
    row = list(rows[keep])
    others = [other for i, other in enumerate(rows) if i != keep]
    filled: list[int] = []
    conflicts: list[int] = []
    for c, cell in enumerate(row):
        if js_trim(cell) != "":
            continue
        candidates = [other[c] for other in others if js_trim(other[c]) != ""]
        if not candidates:
            continue
        row[c] = candidates[0]
        filled.append(c)
        if len({js_trim(value) for value in candidates}) > 1:
            conflicts.append(c)
    return MergedRow(row, filled, conflicts)
