"""CSV import and export. Mirrors web/src/core/csv.ts, which uses Papa Parse.

Delimiter detection and quoting replicate Papa Parse exactly, so both versions read a file
the same way and write byte-identical output (see shared/test-cases/csv.json).
"""

import csv
import io
import re
from pathlib import Path

from ..core.dataset import Dataset
from ..core.encoding import decode_text
from ..core.text import js_trim

# Same candidates and order as Papa Parse (record and unit separators included)
_DELIMITERS = [",", "\t", "|", ";", "\x1e", "\x1f"]
_PREVIEW_ROWS = 10
# Byte order mark: lets Excel detect UTF-8 so accents display correctly
UTF8_BOM = "﻿"


class CsvParseError(Exception):
    pass


def _is_empty_line(row: list[str]) -> bool:
    return js_trim("".join(row)) == ""


def _read(text: str, delimiter: str, limit: int | None = None) -> list[list[str]]:
    reader = csv.reader(
        io.StringIO(text, newline=""), delimiter=delimiter, quotechar='"', doublequote=True, strict=False
    )
    rows = []
    for row in reader:
        rows.append(row)
        if limit is not None and len(rows) >= limit:
            break
    return rows


def guess_delimiter(text: str) -> str:
    """Papa Parse's guessDelimiter: the delimiter whose first rows have the most consistent
    field count wins; ties go to the higher average field count. Defaults to comma."""
    best_delimiter, best_delta, max_field_count = None, None, None
    for delimiter in _DELIMITERS:
        preview = _read(text, delimiter, _PREVIEW_ROWS)
        delta = 0
        field_total = 0
        empty_lines = 0
        previous = None
        for row in preview:
            if _is_empty_line(row):
                empty_lines += 1
                continue
            field_total += len(row)
            if previous is None:
                previous = len(row)
            elif len(row) > 0:
                delta += abs(len(row) - previous)
                previous = len(row)
        counted = len(preview) - empty_lines
        average = field_total / counted if counted > 0 else 0
        if average > 1.99 and (
            best_delta is None or delta < best_delta or (delta == best_delta and average > max_field_count)
        ):
            best_delimiter, best_delta, max_field_count = delimiter, delta, average
    return best_delimiter or ","


def parse_csv_text(text: str, file_name: str, encoding: str = "utf-8") -> Dataset:
    """Parses CSV text. The delimiter is auto-detected and values are kept exactly as written."""
    text = text.removeprefix(UTF8_BOM)
    delimiter = guess_delimiter(text)
    rows = [row for row in _read(text, delimiter) if not _is_empty_line(row)]
    if not rows:
        raise CsvParseError("empty")
    header, *body = rows
    # Pad or trim each row so every row has exactly one cell per column
    normalized = [[row[i] if i < len(row) else "" for i in range(len(header))] for row in body]
    return Dataset(
        file_name=file_name,
        format="csv",
        columns=header,
        rows=normalized,
        row_ids=list(range(len(normalized))),
        delimiter=delimiter,
        encoding=encoding,
    )


def read_csv_file(path: Path) -> Dataset:
    text, encoding = decode_text(path.read_bytes())
    return parse_csv_text(text, path.name, encoding)


def _quote(value: str, delimiter: str) -> str:
    # Papa Parse quotes values with the delimiter, quotes, line breaks or a BOM, or starting/ending with a space
    needs_quotes = (
        delimiter in value
        or any(char in value for char in ('"', "\r", "\n", UTF8_BOM))
        or value.startswith(" ")
        or value.endswith(" ")
    )
    escaped = value.replace('"', '""')
    return f'"{escaped}"' if needs_quotes else escaped


def serialize_csv(dataset: Dataset, delimiter: str | None = None) -> str:
    """Serializes to CSV (by default with the original delimiter). Always UTF-8 with BOM and CRLF."""
    separator = delimiter or dataset.delimiter
    lines = [separator.join(_quote(cell, separator) for cell in row) for row in [dataset.columns, *dataset.rows]]
    return UTF8_BOM + "\r\n".join(lines)


def clean_file_name(file_name: str, extension: str = "csv") -> str:
    """ "clientes.csv" (or .xlsx, .json, .xml) -> "clientes_clean.csv" (or .xlsx)."""
    return re.sub(r"(\.(csv|xlsx|json|xml))?$", f"_clean.{extension}", file_name, count=1, flags=re.IGNORECASE)
