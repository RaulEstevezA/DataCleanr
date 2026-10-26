"""Custom find and replace. Mirrors web/src/core/replace.ts."""

import re
from collections.abc import Callable
from dataclasses import dataclass

from .text import js_trim


@dataclass(frozen=True)
class ReplaceOptions:
    find: str
    replacement: str
    # True: the whole cell must match. False: replace every occurrence inside the text.
    whole_cell: bool
    ignore_case: bool


def create_replace_transform(options: ReplaceOptions) -> Callable[[str], str]:
    """Builds a transform that replaces a user-typed value, e.g. "Transgrau s.l" -> "TransGrau SL".

    In whole-cell mode surrounding spaces are ignored, so "  Transgrau s.l " also matches.
    """
    target = js_trim(options.find) if options.whole_cell else options.find
    if target == "":
        return lambda value: value

    if options.whole_cell:

        def normalize(text: str) -> str:
            return text.lower() if options.ignore_case else text

        normalized_target = normalize(target)
        return lambda value: options.replacement if normalize(js_trim(value)) == normalized_target else value

    pattern = re.compile(re.escape(target), re.IGNORECASE if options.ignore_case else 0)
    # Function replacement so backslashes and group references in the replacement are inserted literally
    return lambda value: pattern.sub(lambda _: options.replacement, value)
