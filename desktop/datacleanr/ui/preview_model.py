"""Table of proposed changes: accept/reject checkbox, row number, original -> proposed."""

import re

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QBrush, QColor, QFont

from ..core.dataset import CellChange, Dataset, row_number
from ..core.text import JS_WHITESPACE
from . import theme

_WHITESPACE = re.compile(f"[{JS_WHITESPACE}]")
ACCEPT, ROW, ORIGINAL, ARROW, PROPOSED = range(5)


def visible_text(value: str, empty: str) -> str:
    """Spaces shown as dots, so trims and collapses can be seen (like the web version)."""
    return _WHITESPACE.sub("·", value) if value else empty


class PreviewModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.dataset: Dataset | None = None
        self.changes: list[CellChange] = []
        # Rejections are stored (not acceptances) so every change is accepted by default
        self.rejected: set[int] = set()
        self.headers = ("", "#", "Original", "", "Proposed")
        self.empty_text = "empty"

    def set_changes(self, dataset: Dataset, changes: list[CellChange]) -> None:
        self.beginResetModel()
        self.dataset = dataset
        self.changes = changes
        self.rejected = set()
        self.endResetModel()

    @property
    def accepted(self) -> list[CellChange]:
        return [change for change in self.changes if change.row not in self.rejected]

    def set_all(self, accepted: bool) -> None:
        self.rejected = set() if accepted else {change.row for change in self.changes}
        if self.changes:
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.changes) - 1, PROPOSED))

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802 (Qt API names)
        return 0 if parent and parent.isValid() else len(self.changes)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return 0 if parent and parent.isValid() else 5

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base = Qt.ItemFlag.ItemIsEnabled
        return base | Qt.ItemFlag.ItemIsUserCheckable if index.column() == ACCEPT else base

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        change = self.changes[index.row()]
        accepted = change.row not in self.rejected
        column = index.column()
        if role == Qt.ItemDataRole.CheckStateRole and column == ACCEPT:
            return Qt.CheckState.Checked if accepted else Qt.CheckState.Unchecked
        if role == Qt.ItemDataRole.DisplayRole:
            if column == ROW and self.dataset:
                return row_number(self.dataset, change.row)
            if column == ORIGINAL:
                return visible_text(change.original, self.empty_text)
            if column == ARROW:
                return "→"
            if column == PROPOSED:
                return visible_text(change.proposed, self.empty_text)
        if role == Qt.ItemDataRole.ToolTipRole and column in (ORIGINAL, PROPOSED):
            return change.original if column == ORIGINAL else change.proposed
        if role == Qt.ItemDataRole.ForegroundRole:
            if not accepted:
                return QBrush(QColor(theme.BORDER))
            if column == PROPOSED:
                return QBrush(QColor(theme.SUCCESS))
            if column in (ORIGINAL, ROW, ARROW):
                return QBrush(QColor(theme.MUTED))
        if role == Qt.ItemDataRole.FontRole and column == PROPOSED and not accepted:
            font = QFont()
            font.setStrikeOut(True)
            return font
        if role == Qt.ItemDataRole.TextAlignmentRole and column == ROW:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:  # noqa: N802
        if role != Qt.ItemDataRole.CheckStateRole or index.column() != ACCEPT:
            return False
        row = self.changes[index.row()].row
        if Qt.CheckState(value) == Qt.CheckState.Checked:
            self.rejected.discard(row)
        else:
            self.rejected.add(row)
        self.dataChanged.emit(self.index(index.row(), 0), self.index(index.row(), PROPOSED))
        return True

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
