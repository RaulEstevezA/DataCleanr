from dataclasses import asdict

import pytest

from datacleanr.core.duplicates import (
    DuplicateOptions,
    SimilarRowsOptions,
    find_duplicate_rows,
    find_similar_rows,
    merge_rows,
)

from .conftest import load_cases

EXACT = load_cases("duplicates.json")
SIMILAR = load_cases("similar-rows.json")
MERGE = load_cases("merge.json")


@pytest.mark.parametrize("case", EXACT, ids=[c["description"] for c in EXACT])
def test_exact_duplicates(case):
    options = DuplicateOptions(case["options"]["columns"], case["options"]["ignoreCaseAndSpaces"])
    assert find_duplicate_rows(case["rows"], options) == case["expected"]


@pytest.mark.parametrize("case", SIMILAR, ids=[c["description"] for c in SIMILAR])
def test_similar_rows(case):
    options = SimilarRowsOptions(
        case["options"]["columns"], case["options"]["threshold"], case["options"]["ignoreLegalForms"]
    )
    groups = find_similar_rows(case["rows"], options)
    assert [group.rows for group in groups] == [group["rows"] for group in case["expected"]]
    for group, expected in zip(groups, case["expected"], strict=True):
        assert group.scores == pytest.approx(expected["scores"], abs=1e-3)


@pytest.mark.parametrize("case", MERGE, ids=[c["description"] for c in MERGE])
def test_merge_rows(case):
    assert asdict(merge_rows(case["rows"], case["keep"])) == case["expected"]
