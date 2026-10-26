import pytest

from datacleanr.io.xlsx_file import EmptySheetError, read_workbook, sheet_to_dataset

from .conftest import SHARED_CASES, load_cases

CASES = load_cases("xlsx.json")
SHEET_CASES = [(f["file"], expected) for f in CASES["files"] for expected in f["sheets"]]


@pytest.mark.parametrize("file_case", CASES["files"], ids=[f["file"] for f in CASES["files"]])
def test_reads_every_sheet_in_order(file_case):
    sheets = read_workbook(SHARED_CASES / file_case["file"])
    assert [s.sheet for s in sheets] == [s["sheet"] for s in file_case["sheets"]]


@pytest.mark.parametrize(("file", "expected"), SHEET_CASES, ids=[f"{f}:{e['sheet']}" for f, e in SHEET_CASES])
def test_sheet(file, expected):
    sheet = next(s for s in read_workbook(SHARED_CASES / file) if s.sheet == expected["sheet"])
    if expected.get("empty"):
        with pytest.raises(EmptySheetError):
            sheet_to_dataset(sheet, file)
        return
    dataset = sheet_to_dataset(sheet, file)
    assert dataset.columns == expected["columns"]
    assert dataset.rows == expected["rows"]
    assert dataset.sheet == expected["sheet"]
