import copy

from datacleanr.core.dataset import (
    Dataset,
    apply_column_changes,
    count_modified_cells,
    preview_column_changes,
    remove_rows,
)
from datacleanr.core.transforms import trim

DATASET = Dataset(
    file_name="test.csv",
    format="csv",
    columns=["Empresa", "Ciudad"],
    rows=[["  TRANSGRAU ", " Valencia"], ["Trans Grau SL", "Bilbao"], ["", "madrid "]],
    row_ids=[0, 1, 2],
)


def test_preview_returns_only_changing_cells():
    changes = preview_column_changes(DATASET, 1, trim)
    assert [(c.row, c.original, c.proposed) for c in changes] == [
        (0, " Valencia", "Valencia"),
        (2, "madrid ", "madrid"),
    ]


def test_apply_only_the_accepted_subset_without_mutating():
    snapshot = copy.deepcopy(DATASET)
    first = preview_column_changes(DATASET, 1, trim)[:1]
    result = apply_column_changes(DATASET, 1, first)
    assert [row[1] for row in result.rows] == ["Valencia", "Bilbao", "madrid "]
    assert DATASET == snapshot


def test_modified_cells_follow_original_rows_after_removing():
    trimmed = apply_column_changes(DATASET, 1, preview_column_changes(DATASET, 1, trim))
    without_first = remove_rows(trimmed, {0})
    assert without_first.row_ids == [1, 2]
    assert count_modified_cells(DATASET, without_first) == 1
