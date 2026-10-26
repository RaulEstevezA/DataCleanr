from dataclasses import asdict

import pytest

from datacleanr.core.similar import SimilarOptions, comparison_key, group_similar_values, similarity

from .conftest import load_cases

CASES = load_cases("similar.json")


@pytest.mark.parametrize("case", CASES["comparisonKey"], ids=[c["description"] for c in CASES["comparisonKey"]])
def test_comparison_key(case):
    assert comparison_key(case["input"], case["ignoreLegalForms"]) == case["expected"]


@pytest.mark.parametrize("case", CASES["similarity"], ids=[f"{c['a']} vs {c['b']}" for c in CASES["similarity"]])
def test_similarity(case):
    assert similarity(case["a"], case["b"]) == pytest.approx(case["expected"], abs=1e-3)


@pytest.mark.parametrize("case", CASES["groups"], ids=[c["description"] for c in CASES["groups"]])
def test_groups(case):
    options = SimilarOptions(case["options"]["threshold"], case["options"]["ignoreLegalForms"])
    assert [asdict(group) for group in group_similar_values(case["values"], options)] == case["expected"]
