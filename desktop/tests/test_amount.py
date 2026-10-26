import pytest

from datacleanr.core.amount import AmountOptions, normalize_amount

from .conftest import load_cases

CASES = load_cases("amount.json")


@pytest.mark.parametrize("case", CASES, ids=[case["description"] for case in CASES])
def test_shared_cases(case):
    options = AmountOptions(
        ambiguous_decimal=case["options"]["ambiguousDecimal"],
        format=case["options"]["format"],
        two_decimals=case["options"]["twoDecimals"],
    )
    result = normalize_amount(case["input"], options)
    assert (result.status, result.value) == (case["expectedStatus"], case["expected"])
    if "expectedCurrency" in case:
        assert result.currency == case["expectedCurrency"]
