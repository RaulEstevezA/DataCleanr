import pytest

from datacleanr.core.dataset import Dataset
from datacleanr.core.split import split_by_completeness, split_row_indexes

from .conftest import load_cases

CASES = load_cases("split.json")


@pytest.mark.parametrize("case", CASES, ids=[c["description"] for c in CASES])
def test_shared_cases(case):
    complete, incomplete = split_row_indexes(case["rows"], case["required"])
    assert {"complete": complete, "incomplete": incomplete} == case["expected"]


def test_keeps_original_row_numbers():
    dataset = Dataset("a.csv", "csv", ["a", "b"], [["1", ""], ["2", "x"]], [4, 7])
    complete, incomplete = split_by_completeness(dataset, [0, 1])
    assert complete.row_ids == [7]
    assert incomplete.row_ids == [4]
