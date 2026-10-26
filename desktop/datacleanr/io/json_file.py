"""JSON import. Mirrors web/src/core/json.ts."""

import json
from pathlib import Path
from typing import Literal

from ..core.dataset import Dataset
from ..core.encoding import decode_text


class JsonImportError(Exception):
    def __init__(self, reason: Literal["invalid", "unsupported", "empty"]):
        super().__init__(reason)
        self.reason = reason


class RawNumber(str):
    """A JSON number kept exactly as written, so big integers and "1.50" are not altered."""


def _reject_constant(name: str):
    # JavaScript's JSON.parse rejects NaN and Infinity; Python's would accept them
    raise ValueError(name)


def _parse_keeping_numbers(text: str):
    return json.loads(text, parse_int=RawNumber, parse_float=RawNumber, parse_constant=_reject_constant)


def _to_json_text(value) -> str:
    """Compact JSON text for arrays inside a cell, writing numbers as they were in the file."""
    if isinstance(value, RawNumber):
        return str(value)
    if isinstance(value, list):
        return "[" + ",".join(_to_json_text(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{_to_json_text(v)}" for k, v in value.items()) + "}"
    return json.dumps(value, ensure_ascii=False)


def _to_cell_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, str):  # includes RawNumber
        return str(value)
    return _to_json_text(value)


def _flatten(obj: dict, prefix: str = "", into: dict | None = None) -> dict:
    """{"a": {"b": 1}} -> {"a.b": 1}. Arrays are not flattened: they stay as JSON text in one cell."""
    into = {} if into is None else into
    for key, value in obj.items():
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            _flatten(value, name, into)
        else:
            into[name] = value
    return into


def parse_json_text(text: str, file_name: str, encoding: str = "utf-8") -> Dataset:
    """Parses JSON that represents a table: a list of objects, a list of lists (first one is
    the header), or an object holding a single such list. Values become text."""
    try:
        root = _parse_keeping_numbers(text.removeprefix("﻿"))
    except ValueError as error:
        raise JsonImportError("invalid") from error

    if isinstance(root, dict):
        if len(root) != 1 or not isinstance(next(iter(root.values())), list):
            raise JsonImportError("unsupported")
        root = next(iter(root.values()))
    if not isinstance(root, list):
        raise JsonImportError("unsupported")
    if not root:
        raise JsonImportError("empty")

    if all(isinstance(item, dict) for item in root):
        flattened = [_flatten(item) for item in root]
        columns = list(dict.fromkeys(name for row in flattened for name in row))
        rows = [[_to_cell_text(row[name]) if name in row else "" for name in columns] for row in flattened]
    elif all(isinstance(item, list) for item in root):
        header, *body = root
        columns = [_to_cell_text(cell) for cell in header]
        rows = [[_to_cell_text(row[i]) if i < len(row) else "" for i in range(len(columns))] for row in body]
    else:
        raise JsonImportError("unsupported")

    return Dataset(
        file_name=file_name,
        format="json",
        columns=columns,
        rows=rows,
        row_ids=list(range(len(rows))),
        encoding=encoding,
    )


def read_json_file(path: Path) -> Dataset:
    text, encoding = decode_text(path.read_bytes())
    return parse_json_text(text, path.name, encoding)
