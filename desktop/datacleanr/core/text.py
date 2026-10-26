"""Whitespace helpers that behave exactly like JavaScript, so both versions agree on edge cases.

Python's str.strip() and regex \\s use a slightly different set of characters than
JavaScript's trim() and \\s (for example the BOM U+FEFF), so the set is spelled out here.
"""

import re

# JavaScript \s: ASCII whitespace, NBSP, Unicode space separators, line/paragraph separators and BOM
JS_WHITESPACE = "\t\n\v\f\r    -     　﻿"

_EDGES = re.compile(f"^[{JS_WHITESPACE}]+|[{JS_WHITESPACE}]+$")
_RUNS = re.compile(f"[{JS_WHITESPACE}]+")


def js_trim(value: str) -> str:
    """Same as JavaScript String.prototype.trim()."""
    return _EDGES.sub("", value)


def collapse_whitespace(value: str) -> str:
    """Replaces every run of whitespace with a single space (JavaScript /\\s+/g)."""
    return _RUNS.sub(" ", value)
