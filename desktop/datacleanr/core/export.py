"""Column types for Excel export. Mirrors web/src/core/export.ts."""

import datetime
import re
from dataclasses import dataclass
from typing import Literal

# Cell type chosen by the user for each column when exporting to Excel
ColumnType = Literal["text", "number", "date", "boolean"]

# Plain dot-decimal numbers without leading zeros: what "Normalize amounts" produces
_NUMBER = re.compile(r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$")
_ISO_DATE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})(?: ([0-9]{2}):([0-9]{2}):([0-9]{2}))?$")
# Excel (like JavaScript and Python floats) keeps 15 significant digits safely
_MAX_SIGNIFICANT_DIGITS = 15
# Excel's date system starts on 1900-01-01: earlier dates cannot be stored as dates
_FIRST_EXCEL_YEAR = 1900


@dataclass(frozen=True)
class TypedCell:
    type: Literal["empty", "text", "number", "date", "boolean"]
    # str for text and date (ISO "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS"), int/float, bool, or None when empty
    value: str | int | float | bool | None = None


def _to_number(value: str) -> int | float | None:
    if not _NUMBER.match(value):
        return None
    integer, _, decimals = value.lstrip("-").partition(".")
    significant = (integer + decimals.rstrip("0")).lstrip("0")
    if len(significant) > _MAX_SIGNIFICANT_DIGITS:
        return None
    return float(value) if "." in value else int(value)


def parse_excel_date(value: str) -> datetime.datetime | None:
    """ISO date (optionally with time) that exists and that Excel can store; None otherwise."""
    match = _ISO_DATE.match(value)
    if not match:
        return None
    year, month, day = int(match[1]), int(match[2]), int(match[3])
    hours, minutes, seconds = (int(part) for part in match.groups(default="0")[3:])
    if year < _FIRST_EXCEL_YEAR:
        return None
    try:
        return datetime.datetime(year, month, day, hours, minutes, seconds)
    except ValueError:
        return None


def _to_boolean(value: str) -> bool | None:
    lower = value.lower()
    return True if lower == "true" else False if lower == "false" else None


def to_typed_cell(value: str, column_type: ColumnType) -> TypedCell:
    """Converts a cell to the requested type. Values that cannot be converted without changing
    or losing information (leading zeros, comma decimals, non-ISO dates...) stay as text,
    so the user never loses data by picking the wrong type."""
    if value == "":
        return TypedCell("empty")
    if column_type == "number" and (number := _to_number(value)) is not None:
        return TypedCell("number", number)
    if column_type == "date" and parse_excel_date(value) is not None:
        return TypedCell("date", value)
    if column_type == "boolean" and (boolean := _to_boolean(value)) is not None:
        return TypedCell("boolean", boolean)
    return TypedCell("text", value)


def count_text_fallbacks(values: list[str], column_type: ColumnType) -> int:
    """Number of non-empty values that would stay as text with the given type."""
    if column_type == "text":
        return 0
    return sum(1 for value in values if to_typed_cell(value, column_type).type == "text")


def suggest_column_type(values: list[str]) -> ColumnType:
    """The first of boolean, date, number that fits every non-empty value; text otherwise."""
    filled = [value for value in values if value != ""]
    if not filled:
        return "text"
    for column_type in ("boolean", "date", "number"):
        if count_text_fallbacks(filled, column_type) == 0:
            return column_type
    return "text"
