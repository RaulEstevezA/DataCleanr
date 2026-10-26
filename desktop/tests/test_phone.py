import pytest

from datacleanr.core.phone import PhoneOptions, normalize_phone

from .conftest import load_cases

CASES = load_cases("phone.json")


@pytest.mark.parametrize("case", CASES, ids=[case["description"] for case in CASES])
def test_shared_cases(case):
    options = PhoneOptions(default_country=case["options"]["defaultCountry"], format=case["options"]["format"])
    result = normalize_phone(case["input"], options)
    assert (result.status, result.value) == (case["expectedStatus"], case["expected"])
