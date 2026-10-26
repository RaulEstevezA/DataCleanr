"""Table model over a Dataset. Qt only asks for the visible cells, so big files scroll smoothly."""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QFontDatabase

from ..core.dataset import Dataset, column_label, row_number
from . import theme


class DatasetTableModel(QAbstractTableModel):
    def __init__(self, empty_text: str = "empty"):
        super().__init__()
        self.dataset: Dataset | None = None
        self.selected_column: int | None = None
        self.empty_text = empty_text
        self._mono = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self._empty_font = QFont()
        self._empty_font.setItalic(True)

    def set_dataset(self, dataset: Dataset | None) -> None:
        self.beginResetModel()
        self.dataset = dataset
        self.endResetModel()

    def set_selected_column(self, column: int | None) -> None:
        self.selected_column = column
        if self.dataset and self.dataset.rows:
            self.dataChanged.emit(
                self.index(0, 0), self.index(len(self.dataset.rows) - 1, len(self.dataset.columns) - 1)
            )
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, max(0, self.columnCount() - 1))

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802 (Qt API names)
        return 0 if (parent and parent.isValid()) or not self.dataset else len(self.dataset.rows)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return 0 if (parent and parent.isValid()) or not self.dataset else len(self.dataset.columns)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not self.dataset:
            return None
        value = self.dataset.rows[index.row()][index.column()]
        if role == Qt.ItemDataRole.DisplayRole:
            return value if value != "" else self.empty_text
        if role == Qt.ItemDataRole.ToolTipRole:
            return value or None
        if role == Qt.ItemDataRole.FontRole:
            return self._empty_font if value == "" else self._mono
        if role == Qt.ItemDataRole.ForegroundRole and value == "":
            return QBrush(QColor(theme.MUTED))
        if role == Qt.ItemDataRole.BackgroundRole and index.column() == self.selected_column:
            return QBrush(QColor(theme.ACCENT_SOFT))
        return None

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not self.dataset:
            return None
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return column_label(self.dataset, section)
            if role == Qt.ItemDataRole.ForegroundRole and section == self.selected_column:
                return QBrush(QColor(theme.ACCENT_TEXT))
        elif role == Qt.ItemDataRole.DisplayRole:
            # Line in the imported file, stable when rows are removed
            return row_number(self.dataset, section)
        return None
