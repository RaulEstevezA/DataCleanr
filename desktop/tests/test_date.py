import pytest

from datacleanr.core.date import DateOptions, normalize_date

from .conftest import load_cases

CASES = load_cases("date.json")


@pytest.mark.parametrize("case", CASES, ids=[case["description"] for case in CASES])
def test_shared_cases(case):
    options = DateOptions(
        input_order=case["options"]["inputOrder"],
        format=case["options"]["format"],
        two_digit_year_limit=case["options"]["twoDigitYearLimit"],
    )
    result = normalize_date(case["input"], options)
    assert (result.status, result.value) == (case["expectedStatus"], case["expected"])
