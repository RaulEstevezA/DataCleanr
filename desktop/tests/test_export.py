from dataclasses import asdict

import pytest

from datacleanr.core.export import suggest_column_type, to_typed_cell

from .conftest import load_cases

CASES = load_cases("xlsx-export.json")


@pytest.mark.parametrize("case", CASES["conversions"], ids=[c["description"] for c in CASES["conversions"]])
def test_conversions(case):
    result = asdict(to_typed_cell(case["value"], case["type"]))
    expected = {"value": None, **case["expected"]}
    assert result == expected


@pytest.mark.parametrize("case", CASES["suggestions"], ids=[c["description"] for c in CASES["suggestions"]])
def test_suggestions(case):
    assert suggest_column_type(case["values"]) == case["expected"]
