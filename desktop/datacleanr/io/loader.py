"""Opens any supported file by its extension. Mirrors the import flow of web/src/App.tsx."""

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from openpyxl.utils.exceptions import InvalidFileException

from ..core.dataset import Dataset
from .csv_file import read_csv_file
from .json_file import read_json_file
from .xlsx_file import EmptySheetError, XlsxSheet, read_workbook, sheet_to_dataset
from .xml_file import read_xml_file

SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".json", ".xml")


class UnsupportedFileError(Exception):
    def __init__(self, reason: Literal["unsupported", "oldExcel"]):
        super().__init__(reason)
        self.reason = reason


class ExcelReadError(Exception):
    """The .xlsx file is damaged, or all its sheets are empty."""


@dataclass(frozen=True)
class LoadedFile:
    dataset: Dataset
    # Every sheet of an Excel workbook, to switch between them; None for other formats
    sheets: list[XlsxSheet] | None = None


def load_file(path: Path) -> LoadedFile:
    extension = path.suffix.lower()
    if extension == ".xls":
        raise UnsupportedFileError("oldExcel")
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileError("unsupported")

    if extension == ".csv":
        return LoadedFile(read_csv_file(path))
    if extension == ".json":
        return LoadedFile(read_json_file(path))
    if extension == ".xml":
        return LoadedFile(read_xml_file(path))

    try:
        sheets = read_workbook(path)
    except (InvalidFileException, zipfile.BadZipFile, KeyError, OSError) as error:
        raise ExcelReadError(path.name) from error
    # Open the first sheet that has data
    for sheet in sheets:
        try:
            return LoadedFile(sheet_to_dataset(sheet, path.name), sheets)
        except EmptySheetError:
            continue
    raise ExcelReadError(path.name)
