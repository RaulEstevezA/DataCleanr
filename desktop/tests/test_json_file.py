import pytest

from datacleanr.io.json_file import JsonImportError, parse_json_text

from .conftest import load_cases

CASES = load_cases("json.json")


@pytest.mark.parametrize("case", CASES, ids=[c["description"] for c in CASES])
def test_shared_cases(case):
    expected = case["expected"]
    if "error" in expected:
        with pytest.raises(JsonImportError) as error:
            parse_json_text(case["input"], "a.json")
        assert error.value.reason == expected["error"]
        return
    dataset = parse_json_text(case["input"], "a.json")
    assert dataset.columns == expected["columns"]
    assert dataset.rows == expected["rows"]
