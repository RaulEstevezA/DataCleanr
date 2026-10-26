import pytest

from datacleanr.io.xml_file import XmlImportError, parse_xml_text

from .conftest import load_cases

CASES = load_cases("xml.json")


@pytest.mark.parametrize("case", CASES, ids=[c["description"] for c in CASES])
def test_shared_cases(case):
    expected = case["expected"]
    if "error" in expected:
        with pytest.raises(XmlImportError) as error:
            parse_xml_text(case["input"], "a.xml")
        assert error.value.reason == expected["error"]
        return
    dataset = parse_xml_text(case["input"], "a.xml")
    assert dataset.columns == expected["columns"]
    assert dataset.rows == expected["rows"]
