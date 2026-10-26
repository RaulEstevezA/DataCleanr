"""Phone number normalization. Mirrors web/src/core/phone.ts.

Uses phonenumbers, the Python port of Google's libphonenumber (the web version uses
libphonenumber-js, a JavaScript port of the same library and metadata).
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import phonenumbers

from .text import js_trim

PhoneFormat = Literal["E164", "INTERNATIONAL", "NATIONAL"]
PhoneStatus = Literal["valid", "invalid", "empty"]

_FORMATS = {
    "E164": phonenumbers.PhoneNumberFormat.E164,
    "INTERNATIONAL": phonenumbers.PhoneNumberFormat.INTERNATIONAL,
    "NATIONAL": phonenumbers.PhoneNumberFormat.NATIONAL,
}


@dataclass(frozen=True)
class PhoneOptions:
    # Country assumed for numbers written without an international prefix, e.g. "ES"
    default_country: str
    format: PhoneFormat


@dataclass(frozen=True)
class PhoneResult:
    status: PhoneStatus
    # Normalized number when valid; the untouched input otherwise
    value: str


def phone_countries() -> list[str]:
    """Region codes with phone metadata, for the default country selector."""
    return sorted(phonenumbers.SUPPORTED_REGIONS)


def normalize_phone(value: str, options: PhoneOptions) -> PhoneResult:
    """Normalizes one phone number. Anything that cannot be normalized safely is returned
    unchanged with status "invalid", so the user can review it by hand."""
    text = js_trim(value)
    if text == "":
        return PhoneResult("empty", value)

    try:
        phone = phonenumbers.parse(text, options.default_country)
    except phonenumbers.NumberParseException:
        return PhoneResult("invalid", value)
    # E.164 has no room for extensions: converting would silently drop them
    if not phonenumbers.is_valid_number(phone) or (options.format == "E164" and phone.extension):
        return PhoneResult("invalid", value)

    if options.format == "E164":
        return PhoneResult("valid", phonenumbers.format_number(phone, _FORMATS["E164"]))
    # A national format for a foreign number would lose its country, so keep it international
    if options.format == "NATIONAL" and phonenumbers.region_code_for_number(phone) == options.default_country:
        return PhoneResult("valid", phonenumbers.format_number(phone, _FORMATS["NATIONAL"]))
    return PhoneResult("valid", phonenumbers.format_number(phone, _FORMATS["INTERNATIONAL"]))


def create_phone_transform(options: PhoneOptions) -> Callable[[str], str]:
    return lambda value: normalize_phone(value, options).value
