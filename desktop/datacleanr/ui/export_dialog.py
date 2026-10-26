"""Export the cleaned data: CSV choosing the delimiter, or Excel choosing the type of each column."""

from pathlib import Path

from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..core.dataset import Dataset, column_label
from ..core.export import count_text_fallbacks, suggest_column_type
from ..io.csv_file import clean_file_name, serialize_csv
from ..io.xlsx_file import write_workbook
from . import theme
from .background import run_in_background
from .i18n import I18n

DELIMITERS = [";", ",", "\t"]
COLUMN_TYPES = ["text", "number", "date", "boolean"]


def write_file(dataset: Dataset, path: Path, file_format: str, delimiter: str, types: list[str]) -> Path:
    if file_format == "csv":
        # newline="" keeps the CRLF line endings written by serialize_csv
        with path.open("w", encoding="utf-8", newline="") as file:
            file.write(serialize_csv(dataset, delimiter))
    else:
        write_workbook(dataset, types, path)
    return path


class ExportDialog(QDialog):
    def __init__(self, i18n: I18n, dataset: Dataset, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.dataset = dataset
        self.saved_path: Path | None = None
        t = i18n.t
        self.setWindowTitle(t.export_title)
        self.resize(820, 620)

        self.csv_button = QPushButton("CSV")
        self.xlsx_button = QPushButton("Excel (.xlsx)")
        formats = QButtonGroup(self)
        for button in (self.csv_button, self.xlsx_button):
            button.setCheckable(True)
            button.setProperty("option", True)
            formats.addButton(button)
            button.clicked.connect(self._format_changed)
        (self.xlsx_button if dataset.format == "xlsx" else self.csv_button).setChecked(True)

        self.delimiter_label = QLabel(t.export_delimiter)
        self.delimiter_label.setProperty("role", "muted")
        self.delimiter = QComboBox()
        for delimiter in DELIMITERS:
            self.delimiter.addItem(t.delimiter_names[delimiter], delimiter)
        self.delimiter.setCurrentIndex(DELIMITERS.index(dataset.delimiter) if dataset.delimiter in DELIMITERS else 1)
        self.csv_hint = QLabel(t.export_csv_hint)
        self.csv_hint.setProperty("role", "muted")
        self.csv_hint.setWordWrap(True)

        self.types_hint = QLabel(t.export_types_hint)
        self.types_hint.setProperty("role", "muted")
        self.types_hint.setWordWrap(True)
        self._column_values = [[row[c] for row in dataset.rows] for c in range(len(dataset.columns))]
        self._suggested = [suggest_column_type(values) for values in self._column_values]
        self.types = QTableWidget(len(dataset.columns), 4)
        self.types.setHorizontalHeaderLabels([t.export_column, t.export_type, t.export_example, ""])
        self.types.verticalHeader().hide()
        self.types.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.types.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        header = self.types.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._combos: list[QComboBox] = []
        for c in range(len(dataset.columns)):
            self.types.setItem(c, 0, QTableWidgetItem(column_label(dataset, c)))
            combo = QComboBox()
            for column_type in COLUMN_TYPES:
                suffix = f" ({t.export_suggested})" if column_type == self._suggested[c] else ""
                combo.addItem(t.column_type_names[column_type] + suffix, column_type)
            combo.setCurrentIndex(COLUMN_TYPES.index(self._suggested[c]))
            combo.currentIndexChanged.connect(lambda _=0, c=c: self._update_fallbacks(c))
            self.types.setCellWidget(c, 1, combo)
            self._combos.append(combo)
            example = next((value for value in self._column_values[c] if value != ""), "")
            self.types.setItem(c, 2, QTableWidgetItem(example))
            self._update_fallbacks(c)
            self.types.setRowHeight(c, 36)

        self.file_name = QLabel()
        self.file_name.setProperty("role", "muted")
        self.error = QLabel()
        self.error.setProperty("role", "error")
        self.error.hide()
        self.cancel_button = QPushButton(t.cancel)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton(t.save_as)
        self.save_button.setProperty("primary", True)
        self.save_button.clicked.connect(self._save)

        formats_row = QHBoxLayout()
        formats_row.addWidget(self.csv_button)
        formats_row.addWidget(self.xlsx_button)
        formats_row.addStretch()
        delimiter_row = QHBoxLayout()
        delimiter_row.addWidget(self.delimiter_label)
        delimiter_row.addWidget(self.delimiter)
        delimiter_row.addStretch()
        footer = QHBoxLayout()
        footer.addWidget(self.file_name)
        footer.addStretch()
        footer.addWidget(self.cancel_button)
        footer.addWidget(self.save_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        layout.addLayout(formats_row)
        layout.addLayout(delimiter_row)
        layout.addWidget(self.csv_hint)
        layout.addWidget(self.types_hint)
        layout.addWidget(self.types, stretch=1)
        layout.addStretch()
        layout.addWidget(self.error)
        layout.addLayout(footer)
        self._format_changed()

    @property
    def file_format(self) -> str:
        return "xlsx" if self.xlsx_button.isChecked() else "csv"

    @property
    def column_types(self) -> list[str]:
        return [combo.currentData() for combo in self._combos]

    def _format_changed(self) -> None:
        csv = self.file_format == "csv"
        for widget in (self.delimiter_label, self.delimiter, self.csv_hint):
            widget.setVisible(csv)
        self.types_hint.setVisible(not csv)
        self.types.setVisible(not csv)
        self.file_name.setText(clean_file_name(self.dataset.file_name, self.file_format))

    def _update_fallbacks(self, column: int) -> None:
        fallbacks = count_text_fallbacks(self._column_values[column], self._combos[column].currentData())
        item = QTableWidgetItem(self.i18n.t.export_fallbacks(fallbacks) if fallbacks else "")
        item.setForeground(QBrush(QColor(theme.WARNING)))
        self.types.setItem(column, 3, item)

    def _save(self) -> None:
        t = self.i18n.t
        suggested = clean_file_name(self.dataset.file_name, self.file_format)
        pattern = "CSV (*.csv)" if self.file_format == "csv" else "Excel (*.xlsx)"
        path, _ = QFileDialog.getSaveFileName(self, t.save_as, suggested, pattern)
        if not path:
            return
        self.save_button.setEnabled(False)
        self.save_button.setText(t.exporting)
        dataset, file_format = self.dataset, self.file_format
        delimiter, types = self.delimiter.currentData(), self.column_types
        run_in_background(
            lambda: write_file(dataset, Path(path), file_format, delimiter, types), self._saved, self._failed
        )

    def _saved(self, path: Path) -> None:
        self.saved_path = path
        self.accept()

    def _failed(self, error: Exception) -> None:
        self.save_button.setEnabled(True)
        self.save_button.setText(self.i18n.t.save_as)
        self.error.setText(self.i18n.t.export_error)
        self.error.show()
