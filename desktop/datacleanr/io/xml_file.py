"""XML import. Mirrors web/src/core/xml.ts.

Parsed with defusedxml: Python's standard parser is vulnerable to malicious files
(entity expansion), and entity declarations are rejected like in the web version.
"""

from pathlib import Path
from typing import Literal
from xml.etree.ElementTree import Element, ParseError

from defusedxml import DefusedXmlException
from defusedxml.ElementTree import fromstring

from ..core.dataset import Dataset
from ..core.encoding import decode_text


class XmlImportError(Exception):
    def __init__(self, reason: Literal["invalid", "unsupported"]):
        super().__init__(reason)
        self.reason = reason


def _local_name(name: str) -> str:
    """ "{urn:ejemplo}total" -> "total": namespaces are dropped, like the web version."""
    return name.rsplit("}", 1)[-1]


def _attributes(element: Element) -> list[tuple[str, str]]:
    # ElementTree already leaves out namespace declarations (xmlns), which are not data
    return [(_local_name(name), value) for name, value in element.attrib.items()]


def _is_structured(element: Element) -> bool:
    """Has structure (child elements or attributes), so it can be a row with several columns."""
    return len(element) > 0 or len(element.attrib) > 0


def _find_records(root: Element) -> list[Element]:
    """The most repeated element name under a single parent. Breadth-first, so on equal counts
    the shallowest (then first) candidate is kept. Structured elements are preferred; plain
    value lists are the fallback."""
    for only_structured in (True, False):
        best: list[Element] = []
        queue = [root]
        while queue:
            element = queue.pop(0)
            by_name: dict[str, list[Element]] = {}
            for child in element:
                queue.append(child)
                if only_structured and not _is_structured(child):
                    continue
                by_name.setdefault(_local_name(child.tag), []).append(child)
            for records in by_name.values():
                if len(records) > len(best):
                    best = records
        if best:
            return best
    return []


def _text(element: Element) -> str:
    return "".join(element.itertext())


def _flatten(element: Element, prefix: str, into: dict[str, str]) -> None:
    """Attributes use "@name", nested elements "parent.child", and repeated children are
    numbered: "telefono", "telefono[2]"."""
    for name, value in _attributes(element):
        into[f"{prefix}@{name}"] = value
    seen: dict[str, int] = {}
    for child in element:
        name = _local_name(child.tag)
        seen[name] = seen.get(name, 0) + 1
        path = prefix + (name if seen[name] == 1 else f"{name}[{seen[name]}]")
        if len(child) > 0:
            _flatten(child, f"{path}.", into)
        else:
            into[path] = _text(child)
            if child.attrib:
                _flatten(child, f"{path}.", into)


def _record_to_cells(record: Element) -> dict[str, str]:
    # A plain value (<item>a</item>) is a one-column row named after the element
    if not _is_structured(record):
        return {_local_name(record.tag): _text(record)}
    cells: dict[str, str] = {}
    _flatten(record, "", cells)
    return cells


def parse_xml_text(text: str, file_name: str, encoding: str = "utf-8") -> Dataset:
    try:
        root = fromstring(text.removeprefix("﻿"))
    except (ParseError, DefusedXmlException, ValueError) as error:
        raise XmlImportError("invalid") from error

    records = _find_records(root)
    if not records:
        raise XmlImportError("unsupported")

    cells_per_record = [_record_to_cells(record) for record in records]
    columns = list(dict.fromkeys(name for cells in cells_per_record for name in cells))
    rows = [[cells.get(name, "") for name in columns] for cells in cells_per_record]
    return Dataset(
        file_name=file_name,
        format="xml",
        columns=columns,
        rows=rows,
        row_ids=list(range(len(rows))),
        encoding=encoding,
    )


def read_xml_file(path: Path) -> Dataset:
    text, encoding = decode_text(path.read_bytes())
    return parse_xml_text(text, path.name, encoding)
