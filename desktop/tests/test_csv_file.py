import pytest

from datacleanr.core.dataset import Dataset
from datacleanr.io.csv_file import CsvParseError, clean_file_name, parse_csv_text, serialize_csv

from .conftest import load_cases

CASES = load_cases("csv.json")


@pytest.mark.parametrize("case", CASES["import"], ids=[c["description"] for c in CASES["import"]])
def test_import(case):
    expected = case["expected"]
    if "error" in expected:
        with pytest.raises(CsvParseError):
            parse_csv_text(case["input"], "a.csv")
        return
    dataset = parse_csv_text(case["input"], "a.csv")
    assert (dataset.delimiter, dataset.columns, dataset.rows) == (
        expected["delimiter"],
        expected["columns"],
        expected["rows"],
    )


@pytest.mark.parametrize("case", CASES["export"], ids=[c["description"] for c in CASES["export"]])
def test_export(case):
    rows = case["rows"]
    dataset = Dataset("a.csv", "csv", case["columns"], rows, list(range(len(rows))), delimiter=case["delimiter"])
    assert serialize_csv(dataset) == case["expected"]


def test_round_trip_keeps_every_value():
    original = parse_csv_text('Empresa;Nota\n  TRANSGRAU ;"a;b"\n;"dice ""hola"""', "a.csv")
    assert parse_csv_text(serialize_csv(original), "a.csv") == original


@pytest.mark.parametrize(
    ("name", "extension", "expected"),
    [
        ("clientes.csv", "csv", "clientes_clean.csv"),
        ("Clientes.CSV", "csv", "Clientes_clean.csv"),
        ("clientes", "csv", "clientes_clean.csv"),
        ("clientes.xlsx", "csv", "clientes_clean.csv"),
        ("clientes.csv", "xlsx", "clientes_clean.xlsx"),
        ("clientes.json", "csv", "clientes_clean.csv"),
        ("clientes.xml", "csv", "clientes_clean.csv"),
    ],
)
def test_clean_file_name(name, extension, expected):
    assert clean_file_name(name, extension) == expected
