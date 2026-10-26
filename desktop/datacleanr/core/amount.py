"""Amount normalization. Mirrors web/src/core/amount.ts.

Works on the digits as text (never as a float), so no precision is lost.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from .text import JS_WHITESPACE, js_trim

# Decimal separator assumed when a value is ambiguous, like "1.234" or "1,234"
DecimalSeparator = Literal[",", "."]
# DOT: 1234.56 · COMMA: 1234,56 · DOT_GROUPED: 1,234.56 · COMMA_GROUPED: 1.234,56
AmountFormat = Literal["DOT", "COMMA", "DOT_GROUPED", "COMMA_GROUPED"]
AmountStatus = Literal["valid", "invalid", "empty"]

_CURRENCIES = {"€": "EUR", "EUR": "EUR", "$": "USD", "USD": "USD", "£": "GBP", "GBP": "GBP"}
_CURRENCY = r"(€|\$|£|EUR|USD|GBP)"
# Thousands separators other than "." and ",": spaces (regular, non-breaking, narrow) and the Swiss apostrophe
_EXTRA_GROUP = "   '"
_WS = f"[{JS_WHITESPACE}]*"
_AMOUNT = re.compile(
    f"^([-+])?{_WS}{_CURRENCY}?{_WS}([-+])?{_WS}([0-9.,{_EXTRA_GROUP}]+?){_WS}{_CURRENCY}?$",
    re.IGNORECASE,
)
_GROUP_SPLIT = re.compile(f"[.,{JS_WHITESPACE}  ']")


@dataclass(frozen=True)
class AmountOptions:
    ambiguous_decimal: DecimalSeparator
    format: AmountFormat
    # Pad to exactly two decimals. Values with more decimals are never rounded: they go to review.
    two_decimals: bool


@dataclass(frozen=True)
class AmountResult:
    status: AmountStatus
    # Formatted number when valid; the untouched input otherwise
    value: str
    # Currency found next to the number (removed from the output), if any
    currency: str | None = None


@dataclass(frozen=True)
class _ParsedAmount:
    negative: bool
    integer: str
    decimals: str
    currency: str | None


# Sentinel for "malformed", distinct from None ("no decimal separator")
_MALFORMED = object()


def _find_decimal_separator(body: str, ambiguous_decimal: str):
    """Picks which separator (if any) is the decimal one. Returns _MALFORMED for malformed values."""
    dots, commas = body.count("."), body.count(",")

    if dots > 0 and commas > 0:
        # Both present: the last one is the decimal separator and must appear once
        decimal = "." if body.rfind(".") > body.rfind(",") else ","
        return decimal if body.count(decimal) == 1 else _MALFORMED
    if dots + commas == 0:
        return None

    separator = "." if dots > 0 else ","
    # Repeated separator can only be thousands: 1.234.567
    if dots + commas > 1:
        return None

    before, after = body.split(separator)
    before_digits = re.sub(r"[^0-9]", "", before)
    has_other_grouping = re.search(r"[^0-9]", before) is not None
    # Only "1-3 digits, separator, exactly 3 digits" (1.234) could be either: use the user's choice
    could_be_thousands = len(after) == 3 and 1 <= len(before_digits) <= 3 and not before_digits.startswith("0")
    if not could_be_thousands or has_other_grouping:
        return separator
    return separator if separator == ambiguous_decimal else None


def _parse_amount(value: str, ambiguous_decimal: str) -> _ParsedAmount | None:
    text = js_trim(value)
    negative = False
    parenthesized = re.match(r"^\((.*)\)$", text)
    if parenthesized:
        negative = True
        text = js_trim(parenthesized[1])

    match = _AMOUNT.match(text)
    if not match:
        return None
    sign_before, currency_before, sign_after, raw_body, currency_after = match.groups()
    if (sign_before and sign_after) or (currency_before and currency_after):
        return None
    sign = sign_before or sign_after
    if sign and parenthesized:
        return None
    if sign == "-":
        negative = True

    body = js_trim(raw_body)
    decimal_separator = _find_decimal_separator(body, ambiguous_decimal)
    if decimal_separator is _MALFORMED:
        return None

    integer_part, decimals = body.split(decimal_separator) if decimal_separator else (body, "")
    if decimal_separator and not re.fullmatch(r"[0-9]+", decimals):
        return None

    # Thousands groups: first group 1-3 digits, the rest exactly 3, a single kind of separator
    groups = _GROUP_SPLIT.split(integer_part)
    separators_used = set(re.sub(r"[0-9]", "", integer_part))
    if len(separators_used) > 1:
        return None
    if len(groups) > 1 and (
        not re.fullmatch(r"[0-9]{1,3}", groups[0]) or any(not re.fullmatch(r"[0-9]{3}", g) for g in groups[1:])
    ):
        return None
    digits = "".join(groups)
    if not re.fullmatch(r"[0-9]*", digits) or (digits == "" and decimals == ""):
        return None

    code = (currency_before or currency_after or "").upper()
    return _ParsedAmount(
        negative=negative,
        integer=re.sub(r"^0+(?=[0-9])", "", digits) or "0",
        decimals=decimals,
        currency=_CURRENCIES[code] if code else None,
    )


def _group_thousands(integer: str, separator: str) -> str:
    return re.sub(r"\B(?=([0-9]{3})+(?![0-9]))", separator, integer)


def normalize_amount(value: str, options: AmountOptions) -> AmountResult:
    """Normalizes one amount. Anything malformed or ambiguous goes to review unchanged."""
    if js_trim(value) == "":
        return AmountResult("empty", value)

    parsed = _parse_amount(value, options.ambiguous_decimal)
    if parsed is None:
        return AmountResult("invalid", value)

    decimals = parsed.decimals
    if options.two_decimals:
        if len(decimals) > 2:
            return AmountResult("invalid", value)
        decimals = decimals.ljust(2, "0")

    decimal_separator = "." if options.format in ("DOT", "DOT_GROUPED") else ","
    if options.format == "DOT_GROUPED":
        integer = _group_thousands(parsed.integer, ",")
    elif options.format == "COMMA_GROUPED":
        integer = _group_thousands(parsed.integer, ".")
    else:
        integer = parsed.integer

    formatted = f"{'-' if parsed.negative else ''}{integer}{decimal_separator + decimals if decimals else ''}"
    return AmountResult("valid", formatted, parsed.currency)


def create_amount_transform(options: AmountOptions) -> Callable[[str], str]:
    return lambda value: normalize_amount(value, options).value
