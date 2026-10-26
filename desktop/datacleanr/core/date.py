"""Date normalization. Mirrors web/src/core/date.ts."""

import datetime
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from .text import js_trim

# How to read ambiguous dates like 03/04/2024. Year-first dates are always year/month/day.
DateInputOrder = Literal["DMY", "MDY"]
DateFormat = Literal["ISO", "DMY", "MDY"]
DateStatus = Literal["valid", "invalid", "empty"]

DEFAULT_TWO_DIGIT_YEAR_LIMIT = 29

# \2 forces the same separator throughout: "13/07-2024" is rejected. ASCII digits only, like JavaScript \d.
_YEAR_FIRST = re.compile(r"^([0-9]{4})([-/.])([0-9]{1,2})\2([0-9]{1,2})$")
_YEAR_LAST = re.compile(r"^([0-9]{1,2})([-/.])([0-9]{1,2})\2([0-9]{2}|[0-9]{4})$")


@dataclass(frozen=True)
class DateOptions:
    input_order: DateInputOrder
    format: DateFormat
    # Two-digit years from 00 up to this value are 20xx; above it, 19xx. Excel uses 29.
    two_digit_year_limit: int = DEFAULT_TWO_DIGIT_YEAR_LIMIT


@dataclass(frozen=True)
class DateResult:
    status: DateStatus
    # Formatted date when valid; the untouched input otherwise
    value: str


def _expand_year(year: str, limit: int) -> int:
    value = int(year)
    if len(year) == 4:
        return value
    return 2000 + value if value <= limit else 1900 + value


def normalize_date(value: str, options: DateOptions) -> DateResult:
    """Normalizes one date. Anything ambiguous or unsupported (times, month names...)
    is returned unchanged with status "invalid" so the user can review it by hand."""
    text = js_trim(value)
    if text == "":
        return DateResult("empty", value)

    if year_first := _YEAR_FIRST.match(text):
        year, month, day = int(year_first[1]), int(year_first[3]), int(year_first[4])
    elif year_last := _YEAR_LAST.match(text):
        first, second = int(year_last[1]), int(year_last[3])
        day, month = (first, second) if options.input_order == "DMY" else (second, first)
        year = _expand_year(year_last[4], options.two_digit_year_limit)
    else:
        return DateResult("invalid", value)

    try:
        date = datetime.date(year, month, day)
    except ValueError:
        return DateResult("invalid", value)

    formatted = {
        "ISO": f"{date.year:04d}-{date.month:02d}-{date.day:02d}",
        "DMY": f"{date.day:02d}/{date.month:02d}/{date.year:04d}",
        "MDY": f"{date.month:02d}/{date.day:02d}/{date.year:04d}",
    }[options.format]
    return DateResult("valid", formatted)


def create_date_transform(options: DateOptions) -> Callable[[str], str]:
    return lambda value: normalize_date(value, options).value
