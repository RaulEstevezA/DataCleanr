"""Export the cleaned data: CSV choosing the delimiter, or Excel choosing the type of each column."""

from pathlib import Path

from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
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
from ..core.split import split_by_completeness
from ..io.csv_file import clean_file_name, part_path, serialize_csv
from ..io.xlsx_file import write_workbook
from . import theme
from .background import run_in_background
from .flow_layout import FlowLayout
from .i18n import I18n
from .paths import in_downloads

DELIMITERS = [";", ",", "\t"]
COLUMN_TYPES = ["text", "number", "date", "boolean"]


def write_file(
    parts: list[tuple[str | None, str, Dataset]], path: Path, file_format: str, delimiter: str, types: list[str]
) -> list[Path]:
    """Writes the export. `parts` are (file suffix, sheet name, dataset): one entry for a normal
    export, or the complete/incomplete parts. CSV writes one file per part, next to `path`;
    Excel writes one file with one sheet per part."""
    if file_format == "xlsx":
        write_workbook([(sheet, dataset) for _, sheet, dataset in parts], types, path)
        return [path]
    written = []
    for suffix, _, dataset in parts:
        target = part_path(path, suffix) if suffix else path
        # newline="" keeps the CRLF line endings written by serialize_csv
        with target.open("w", encoding="utf-8", newline="") as file:
            file.write(serialize_csv(dataset, delimiter))
        written.append(target)
    return written


class ExportDialog(QDialog):
    def __init__(self, i18n: I18n, dataset: Dataset, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.dataset = dataset
        self.saved_path: Path | None = None
        self.saved_paths: list[Path] = []
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

        self.split = QCheckBox(t.export_split)
        self.split.toggled.connect(self._split_changed)
        self.required_label = QLabel(t.export_required)
        self.required_label.setProperty("role", "muted")
        self.required_label.setWordWrap(True)
        self.required = FlowLayout(spacing=8)
        self.required_buttons: list[QPushButton] = []
        for c in range(len(dataset.columns)):
            button = QPushButton(column_label(dataset, c), self)
            button.setProperty("tag", True)
            button.setCheckable(True)
            button.setChecked(True)
            button.clicked.connect(self._split_changed)
            self.required.addWidget(button)
            self.required_buttons.append(button)
        self.split_counts = QLabel()
        self.split_counts.setProperty("role", "muted")
        self.split_hint = QLabel()
        self.split_hint.setProperty("role", "muted")
        self.split_hint.setWordWrap(True)

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
        layout.addWidget(self.split)
        layout.addWidget(self.required_label)
        layout.addLayout(self.required)
        layout.addWidget(self.split_counts)
        layout.addWidget(self.split_hint)
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
        self._split_changed()

    def _required_columns(self) -> list[int]:
        return [c for c, button in enumerate(self.required_buttons) if button.isChecked()]

    def parts(self) -> list[tuple[str | None, str, Dataset]]:
        """(file suffix, sheet name, dataset) to export; empty parts are left out."""
        t = self.i18n.t
        if not self.split.isChecked():
            return [(None, self.dataset.sheet or "Data", self.dataset)]
        complete, incomplete = split_by_completeness(self.dataset, self._required_columns())
        parts = [("complete", t.sheet_complete, complete), ("incomplete", t.sheet_incomplete, incomplete)]
        return [part for part in parts if part[2].rows]

    def _split_changed(self) -> None:
        t = self.i18n.t
        split = self.split.isChecked()
        for widget in (self.required_label, self.split_counts, self.split_hint, *self.required_buttons):
            widget.setVisible(split)
        if split:
            complete, incomplete = split_by_completeness(self.dataset, self._required_columns())
            hint = t.export_split_csv_hint if self.file_format == "csv" else t.export_split_xlsx_hint
            if not complete.rows or not incomplete.rows:
                hint = f"{t.split_single_part} {hint}"
            self.split_counts.setText(t.split_counts(len(complete.rows), len(incomplete.rows)))
            self.split_hint.setText(hint)
        if split and self.file_format == "csv":
            names = [clean_file_name(self.dataset.file_name, "csv", suffix) for suffix, _, _ in self.parts()]
        else:
            names = [clean_file_name(self.dataset.file_name, self.file_format)]
        self.file_name.setText(" · ".join(names))

    def _update_fallbacks(self, column: int) -> None:
        fallbacks = count_text_fallbacks(self._column_values[column], self._combos[column].currentData())
        item = QTableWidgetItem(self.i18n.t.export_fallbacks(fallbacks) if fallbacks else "")
        item.setForeground(QBrush(QColor(theme.WARNING)))
        self.types.setItem(column, 3, item)

    def _save(self) -> None:
        t = self.i18n.t
        suggested = clean_file_name(self.dataset.file_name, self.file_format)
        pattern = "CSV (*.csv)" if self.file_format == "csv" else "Excel (*.xlsx)"
        path, _ = QFileDialog.getSaveFileName(self, t.save_as, in_downloads(suggested), pattern)
        if not path:
            return
        self.save_button.setEnabled(False)
        self.save_button.setText(t.exporting)
        parts, file_format = self.parts(), self.file_format
        delimiter, types = self.delimiter.currentData(), self.column_types
        run_in_background(
            lambda: write_file(parts, Path(path), file_format, delimiter, types), self._saved, self._failed
        )

    def _saved(self, paths: list[Path]) -> None:
        self.saved_paths = paths
        self.saved_path = paths[0]
        self.accept()

    def _failed(self, error: Exception) -> None:
        self.save_button.setEnabled(True)
        self.save_button.setText(self.i18n.t.save_as)
        self.error.setText(self.i18n.t.export_error)
        self.error.show()
