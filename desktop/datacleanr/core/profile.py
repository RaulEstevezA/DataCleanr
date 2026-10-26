"""Cleaning profiles: replayable steps saved as JSON. Mirrors web/src/core/profile.ts.

Both versions read and write the same format. Steps are kept as plain dicts with the same
field names as the JSON file, so nothing is lost or renamed between versions.
"""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import Any, Literal

from .amount import AmountOptions, create_amount_transform
from .dataset import Dataset, apply_column_changes, preview_column_changes, remove_rows
from .date import DateOptions, create_date_transform
from .duplicates import DuplicateOptions, find_duplicate_rows, merge_rows
from .phone import PhoneOptions, create_phone_transform
from .replace import ReplaceOptions, create_replace_transform
from .transforms import TRANSFORMS

PROFILE_FORMAT = "datacleanr-profile"
PROFILE_VERSION = 1

Step = dict[str, Any]


class ProfileError(Exception):
    def __init__(self, reason: Literal["invalid", "version", "step"], step: int | None = None):
        super().__init__(reason if step is None else f"{reason} {step}")
        self.reason = reason
        # Index of the offending step, for reason "step"
        self.step = step


@dataclass(frozen=True)
class Profile:
    name: str
    steps: list[Step]


def _is_str(value: Any) -> bool:
    return isinstance(value, str)


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _one_of(*options: str) -> Callable[[Any], bool]:
    return lambda value: value in options


def _is_year_limit(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 99


# Required fields (besides "type") and how to check them, per step type
_STEP_FIELDS: dict[str, dict[str, Callable[[Any], bool]]] = {
    "transform": {"column": _is_str, "transform": _one_of(*TRANSFORMS)},
    "replace": {
        "column": _is_str,
        "find": _is_str,
        "replacement": _is_str,
        "wholeCell": _is_bool,
        "ignoreCase": _is_bool,
    },
    "phone": {
        "column": _is_str,
        "defaultCountry": lambda v: _is_str(v) and re.fullmatch(r"[A-Z]{2}", v) is not None,
        "format": _one_of("E164", "INTERNATIONAL", "NATIONAL"),
    },
    "date": {
        "column": _is_str,
        "inputOrder": _one_of("DMY", "MDY"),
        "format": _one_of("ISO", "DMY", "MDY"),
        "twoDigitYearLimit": _is_year_limit,
    },
    "amount": {
        "column": _is_str,
        "ambiguousDecimal": _one_of(",", "."),
        "format": _one_of("DOT", "COMMA", "DOT_GROUPED", "COMMA_GROUPED"),
        "twoDecimals": _is_bool,
    },
    "map": {
        "column": _is_str,
        "mapping": lambda v: (
            isinstance(v, list)
            and all(isinstance(m, dict) and _is_str(m.get("from")) and _is_str(m.get("to")) for m in v)
        ),
    },
    "removeDuplicates": {
        "columns": lambda v: isinstance(v, list) and len(v) > 0 and all(_is_str(c) for c in v),
        "ignoreCaseAndSpaces": _is_bool,
        "merge": _is_bool,
    },
}


def _validate_step(step: Any, index: int) -> Step:
    fields = _STEP_FIELDS.get(step.get("type")) if isinstance(step, dict) else None
    if fields is None or not all(check(step.get(name)) for name, check in fields.items()):
        raise ProfileError("step", index)
    return step


def parse_profile(text: str) -> Profile:
    """Parses and validates a profile file. Unknown extra fields are ignored."""
    try:
        data = json.loads(text.removeprefix("﻿"))
    except json.JSONDecodeError as error:
        raise ProfileError("invalid") from error
    if (
        not isinstance(data, dict)
        or data.get("format") != PROFILE_FORMAT
        or not isinstance(data.get("steps"), list)
        or not _is_str(data.get("name"))
    ):
        raise ProfileError("invalid")
    if data.get("version") != PROFILE_VERSION:
        raise ProfileError("version")
    return Profile(data["name"], [_validate_step(step, i) for i, step in enumerate(data["steps"])])


def serialize_profile(profile: Profile) -> str:
    data = {"format": PROFILE_FORMAT, "version": PROFILE_VERSION, "name": profile.name, "steps": profile.steps}
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


@dataclass(frozen=True)
class StepResult:
    step: Step
    status: Literal["applied", "skipped"]
    # Dataset after this step (the same object when nothing changed)
    dataset: Dataset
    # Cells changed, or rows removed for removeDuplicates
    count: int = 0
    reason: Literal["missingColumn"] | None = None
    # Empty cells filled when merging duplicates
    filled: int = field(default=0)


def _cell_transform(step: Step) -> Callable[[str], str]:
    match step["type"]:
        case "transform":
            return TRANSFORMS[step["transform"]]
        case "replace":
            return create_replace_transform(
                ReplaceOptions(step["find"], step["replacement"], step["wholeCell"], step["ignoreCase"])
            )
        case "phone":
            return create_phone_transform(PhoneOptions(step["defaultCountry"], step["format"]))
        case "date":
            return create_date_transform(DateOptions(step["inputOrder"], step["format"], step["twoDigitYearLimit"]))
        case "amount":
            return create_amount_transform(AmountOptions(step["ambiguousDecimal"], step["format"], step["twoDecimals"]))
        case "map":
            mapping = {rule["from"]: rule["to"] for rule in step["mapping"]}
            return lambda value: mapping.get(value, value)
    raise ProfileError("step")


def _run_step(dataset: Dataset, step: Step) -> StepResult:
    # Columns are matched by name; with duplicated names, the first one is used
    def index_of(name: str) -> int:
        return dataset.columns.index(name) if name in dataset.columns else -1

    if step["type"] == "removeDuplicates":
        columns = [index_of(name) for name in step["columns"]]
        if any(c < 0 for c in columns):
            return StepResult(step, "skipped", dataset, reason="missingColumn")
        groups = find_duplicate_rows(dataset.rows, DuplicateOptions(columns, step["ignoreCaseAndSpaces"]))
        rows = list(dataset.rows)
        remove: set[int] = set()
        filled = 0
        for group in groups:
            if step["merge"]:
                merged = merge_rows([dataset.rows[r] for r in group], 0)
                rows[group[0]] = merged.row
                filled += len(merged.filled)
            remove.update(group[1:])
        updated = remove_rows(replace(dataset, rows=rows), remove)
        return StepResult(step, "applied", updated, count=len(remove), filled=filled)

    column = index_of(step["column"])
    if column < 0:
        return StepResult(step, "skipped", dataset, reason="missingColumn")
    changes = preview_column_changes(dataset, column, _cell_transform(step))
    return StepResult(step, "applied", apply_column_changes(dataset, column, changes), count=len(changes))


def run_profile(dataset: Dataset, profile: Profile) -> list[StepResult]:
    """Runs every step in order. Each result carries the dataset after that step, for the history."""
    results = []
    current = dataset
    for step in profile.steps:
        result = _run_step(current, step)
        results.append(result)
        current = result.dataset
    return results
