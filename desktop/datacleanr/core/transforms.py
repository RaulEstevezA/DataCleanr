"""Basic text transformations. Mirrors web/src/core/transforms.ts.

Each one is a pure function: it never mutates the dataset, it only computes the
proposed value for a single cell.
"""

import re
from collections.abc import Callable

from .text import JS_WHITESPACE, collapse_whitespace, js_trim

# A letter at the start or right after whitespace or a hyphen: "jean-luc PÉREZ" -> "Jean-Luc Pérez"
_WORD_START = re.compile(f"(^|[{JS_WHITESPACE}-])([^\\W\\d_])")


def trim(value: str) -> str:
    return js_trim(value)


def collapse_spaces(value: str) -> str:
    """Replaces any run of whitespace (spaces, tabs, non-breaking spaces) with a single space."""
    return collapse_whitespace(value)


def lowercase(value: str) -> str:
    return value.lower()


def uppercase(value: str) -> str:
    return value.upper()


def title_case(value: str) -> str:
    return _WORD_START.sub(lambda match: match.group(1) + match.group(2).upper(), value.lower())


# Keys match the transform ids used in the shared test cases and in cleaning profiles
TRANSFORMS: dict[str, Callable[[str], str]] = {
    "trim": trim,
    "collapseSpaces": collapse_spaces,
    "lowercase": lowercase,
    "uppercase": uppercase,
    "titleCase": title_case,
}
