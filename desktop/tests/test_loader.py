import pytest

from datacleanr.io.loader import ExcelReadError, UnsupportedFileError, load_file


def test_csv(tmp_path):
    path = tmp_path / "a.csv"
    path.write_bytes("Empresa;Ciudad\nTransgrau;Valencia\n".encode("cp1252"))
    loaded = load_file(path)
    assert loaded.dataset.rows == [["Transgrau", "Valencia"]]
    assert loaded.sheets is None


def test_excel_opens_first_sheet_with_data(shared_file):
    loaded = load_file(shared_file("sample.xlsx"))
    assert loaded.dataset.sheet == "Clientes"
    assert [sheet.sheet for sheet in loaded.sheets] == ["Clientes", "Proveedores", "Vacía"]


def test_json_and_xml(tmp_path):
    (tmp_path / "a.json").write_text('[{"a": 1}]', encoding="utf-8")
    (tmp_path / "a.xml").write_text("<l><r><a>1</a></r></l>", encoding="utf-8")
    assert load_file(tmp_path / "a.json").dataset.rows == [["1"]]
    assert load_file(tmp_path / "a.xml").dataset.rows == [["1"]]


@pytest.mark.parametrize(("name", "reason"), [("old.xls", "oldExcel"), ("notes.txt", "unsupported")])
def test_unsupported(tmp_path, name, reason):
    (tmp_path / name).write_text("x")
    with pytest.raises(UnsupportedFileError) as error:
        load_file(tmp_path / name)
    assert error.value.reason == reason


def test_damaged_excel(tmp_path):
    (tmp_path / "broken.xlsx").write_text("not a zip")
    with pytest.raises(ExcelReadError):
        load_file(tmp_path / "broken.xlsx")
