"""Main window: header with the language switcher and the current page."""

from pathlib import Path

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.dataset import Dataset, column_label, count_modified_cells
from ..core.history import History, create_history, push_entry, redo, undo
from ..io.csv_file import CsvParseError
from ..io.json_file import JsonImportError
from ..io.loader import ExcelReadError, LoadedFile, UnsupportedFileError, load_file
from ..io.xlsx_file import EmptySheetError, XlsxSheet, sheet_to_dataset
from ..io.xml_file import XmlImportError
from .background import run_in_background
from .i18n import MESSAGES, I18n
from .session import CellsOperation, HistoryStep, ImportOperation
from .start_page import StartPage
from .workspace import WorkspacePage


class LanguageSwitcher(QWidget):
    def __init__(self, i18n: I18n):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        group = QButtonGroup(self)
        self._buttons = {}
        for code in MESSAGES:
            button = QPushButton(code.upper())
            button.setProperty("lang", True)
            button.setCheckable(True)
            button.clicked.connect(lambda _=False, code=code: i18n.set_language(code))
            group.addButton(button)
            layout.addWidget(button)
            self._buttons[code] = button
        self._i18n = i18n
        i18n.changed.connect(self._sync)
        self._sync()

    def _sync(self) -> None:
        self._buttons[self._i18n.language].setChecked(True)


class MainWindow(QMainWindow):
    def __init__(self, i18n: I18n):
        super().__init__()
        self._i18n = i18n
        self.setWindowTitle("DataCleanr")
        self.resize(1200, 820)

        header = QHBoxLayout()
        header.setContentsMargins(24, 16, 24, 8)
        brand = QLabel("DataCleanr")
        brand.setStyleSheet("font-weight: 600;")
        header.addWidget(brand)
        header.addStretch()
        header.addWidget(LanguageSwitcher(i18n))

        self.start_page = StartPage(i18n)
        self.start_page.file_selected.connect(self.open_file)
        self.workspace = WorkspacePage(i18n)
        self.workspace.import_another.connect(self.show_start)
        self.workspace.sheet_selected.connect(self.select_sheet)
        self.workspace.applied.connect(self.apply_cells)
        self.workspace.undo.connect(lambda: self.move_in_history(undo))
        self.workspace.redo.connect(lambda: self.move_in_history(redo))
        self.pages = QStackedWidget()
        self.pages.addWidget(self.start_page)
        self.pages.addWidget(self.workspace)

        # Every applied operation adds a new dataset version; the first entry is the untouched original
        self.history: History[HistoryStep] | None = None
        # Every sheet of the imported Excel file, to switch between them; None for other formats
        self.sheets: list[XlsxSheet] | None = None

        # Text fields keep their own undo: Qt gives them the shortcut first when they have focus
        for sequences, move in ((QKeySequence.StandardKey.Undo, undo), (QKeySequence.StandardKey.Redo, redo)):
            action = QAction(self)
            action.setShortcuts(QKeySequence.keyBindings(sequences))
            action.triggered.connect(lambda _=False, move=move: self.move_in_history(move))
            self.addAction(action)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.pages)
        self.setCentralWidget(central)

    def open_file(self, path: Path) -> None:
        drop_zone = self.start_page.drop_zone
        drop_zone.show_error(None)
        drop_zone.set_loading(True)
        run_in_background(lambda: load_file(path), self._file_loaded, self._file_failed)

    def _file_loaded(self, loaded: LoadedFile) -> None:
        self.start_page.drop_zone.set_loading(False)
        self.sheets = loaded.sheets
        self._show_dataset(loaded.dataset)

    def _file_failed(self, error: Exception) -> None:
        self.start_page.drop_zone.set_loading(False)
        self.start_page.drop_zone.show_error(self._error_message(error))

    def _error_message(self, error: Exception) -> str:
        t = self._i18n.t
        if isinstance(error, UnsupportedFileError):
            return t.error_old_excel if error.reason == "oldExcel" else t.error_unsupported
        if isinstance(error, CsvParseError):
            return t.error_parse_csv
        if isinstance(error, ExcelReadError):
            return t.error_parse_excel
        if isinstance(error, JsonImportError):
            return t.error_parse_json[error.reason]
        if isinstance(error, XmlImportError):
            return t.error_parse_xml[error.reason]
        return t.error_read

    @property
    def dataset(self) -> Dataset | None:
        return self.history.current.dataset if self.history else None

    def _show_dataset(self, dataset: Dataset) -> None:
        self.history = create_history(HistoryStep(dataset, ImportOperation()))
        self._refresh()
        self.pages.setCurrentWidget(self.workspace)

    def _refresh(self, keep_column: bool = False) -> None:
        original = self.history.entries[0].dataset
        current = self.dataset
        sheets = [sheet.sheet for sheet in self.sheets] if self.sheets else None
        self.workspace.set_dataset(current, sheets, count_modified_cells(original, current), keep_column)
        self.workspace.set_history_state(self.history.can_undo, self.history.can_redo)

    def apply_cells(self, updated: Dataset, count: int, action: str, profile_step: dict) -> None:
        column = self.workspace.selected_column
        self.history = push_entry(
            self.history, HistoryStep(updated, CellsOperation(column, action, count), profile_step)
        )
        self._refresh(keep_column=True)
        self.workspace.show_notice(self._i18n.t.changes_applied(count, column_label(updated, column)))

    def move_in_history(self, move) -> None:
        if not self.history or self.pages.currentWidget() is not self.workspace:
            return
        self.history = move(self.history)
        self._refresh(keep_column=True)
        self.workspace.show_notice(None)

    def select_sheet(self, name: str) -> None:
        sheet = next((sheet for sheet in self.sheets or [] if sheet.sheet == name), None)
        if not sheet or not self.dataset:
            return
        try:
            self._show_dataset(sheet_to_dataset(sheet, self.dataset.file_name))
        except EmptySheetError:
            self.workspace.summary.sheet_combo.setCurrentText(self.dataset.sheet or "")
            self.statusBar().showMessage(self._i18n.t.empty_sheet(name), 5000)

    def show_start(self) -> None:
        self.history = None
        self.sheets = None
        self.pages.setCurrentWidget(self.start_page)
