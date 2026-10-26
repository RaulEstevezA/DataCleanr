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


def test_write_and_read_back_without_shifting_or_losing_values(tmp_path):
    from openpyxl import load_workbook

    from datacleanr.core.dataset import Dataset
    from datacleanr.io.xlsx_file import write_workbook

    dataset = Dataset(
        "a.csv",
        "csv",
        ["ID", "Fecha", "Importe", "Activo", "Código", "Nota"],
        [
            ["1001", "2024-07-13", "5837.32", "TRUE", "007", "=1+1"],
            ["1002", "2024-01-12 10:30:00", "-0.1", "false", "46001", "texto"],
            ["", "13/07/2024", "1234,56", "", "", ""],
        ],
        [0, 1, 2],
    )
    path = tmp_path / "out.xlsx"
    write_workbook([("Data", dataset)], ["number", "date", "number", "boolean", "text", "text"], path)

    back = sheet_to_dataset(read_workbook(path)[0], "out.xlsx")
    assert back.sheet == "Data"
    assert back.columns == dataset.columns
    assert back.rows == [
        ["1001", "2024-07-13", "5837.32", "TRUE", "007", "=1+1"],
        ["1002", "2024-01-12 10:30:00", "-0.1", "FALSE", "46001", "texto"],
        # Values that cannot be converted stay as text, untouched
        ["", "13/07/2024", "1234,56", "", "", ""],
    ]
    sheet = load_workbook(path).active
    assert sheet.freeze_panes == "A2"
    assert sheet["A1"].font.bold
    assert sheet["F2"].data_type == "s"
