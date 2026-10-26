"""Main window: header with the language switcher and the current page."""

from pathlib import Path

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.dataset import Dataset, column_label, count_modified_cells
from ..core.history import History, create_history, go_to, push_entry, redo, undo
from ..core.profile import ProfileError, parse_profile, run_profile
from ..io.csv_file import CsvParseError
from ..io.json_file import JsonImportError
from ..io.loader import ExcelReadError, LoadedFile, UnsupportedFileError, load_file
from ..io.xlsx_file import EmptySheetError, XlsxSheet, sheet_to_dataset
from ..io.xml_file import XmlImportError
from .background import run_in_background
from .duplicates_dialog import DuplicatesDialog
from .export_dialog import ExportDialog
from .history_dialog import HistoryDialog
from .i18n import MESSAGES, I18n
from .profile_dialog import ProfileDialog
from .session import CellsOperation, HistoryStep, ImportOperation, RemoveRowsOperation
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
        self.setAcceptDrops(True)

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
        self.workspace.find_duplicates.connect(self.find_duplicates)
        self.workspace.export.connect(self.export)
        self.workspace.show_history.connect(self.show_history)
        self.workspace.load_profile.connect(self.load_profile)
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

    # The whole window accepts dropped files, on any screen and also while it is in the background

    def dragEnterEvent(self, event) -> None:  # noqa: N802 (Qt API names)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: N802
        urls = event.mimeData().urls()
        if not urls or not urls[0].isLocalFile():
            return
        event.acceptProposedAction()
        self.raise_()
        self.activateWindow()
        if self.pages.currentWidget() is self.workspace and not self.confirm_discard():
            return
        self.open_file(Path(urls[0].toLocalFile()))

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
        message = self._error_message(error)
        # A file dropped onto the workspace fails there, where the user is looking
        if self.pages.currentWidget() is self.workspace:
            self.workspace.show_notice(message, warning=True)
        else:
            self.start_page.drop_zone.show_error(message)

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
        removed = len(original.rows) - len(current.rows)
        self.workspace.set_dataset(current, sheets, count_modified_cells(original, current), keep_column, removed)
        self.workspace.set_history_state(self.history.can_undo, self.history.can_redo, len(self.history.entries) - 1)

    def apply_cells(self, updated: Dataset, count: int, action: str, profile_step: dict) -> None:
        column = self.workspace.selected_column
        self.history = push_entry(
            self.history, HistoryStep(updated, CellsOperation(column, action, count), profile_step)
        )
        self._refresh(keep_column=True)
        self.workspace.show_notice(self._i18n.t.changes_applied(count, column_label(updated, column)))

    def find_duplicates(self) -> None:
        if not self.dataset:
            return
        dialog = DuplicatesDialog(self._i18n, self.dataset, self)
        if dialog.exec() and dialog.result:
            self.apply_removal(dialog.result)

    def export(self) -> None:
        if not self.dataset:
            return
        dialog = ExportDialog(self._i18n, self.dataset, self)
        if dialog.exec() and dialog.saved_path:
            self.workspace.show_notice(self._i18n.t.saved(str(dialog.saved_path)))

    def apply_removal(self, result) -> None:
        operation = RemoveRowsOperation(result.mode, result.removed, result.filled)
        self.history = push_entry(self.history, HistoryStep(result.dataset, operation, result.profile_step))
        self._refresh()
        self.workspace.show_notice(self._i18n.t.rows_removed(result.removed, result.filled))

    def show_history(self) -> None:
        if not self.history:
            return
        dialog = HistoryDialog(self._i18n, self.history, self)
        dialog.exec()
        if dialog.saved_path:
            self.workspace.show_notice(self._i18n.t.profile_saved(str(dialog.saved_path)))
        if dialog.go_to_index is not None and dialog.go_to_index != self.history.index:
            self.move_in_history(lambda history: go_to(history, dialog.go_to_index))

    def load_profile(self, path: Path | None = None) -> None:
        if not self.dataset:
            return
        t = self._i18n.t
        if path is None:
            chosen, _ = QFileDialog.getOpenFileName(self, t.load_profile, "", "JSON (*.json)")
            if not chosen:
                return
            path = Path(chosen)
        try:
            profile = parse_profile(path.read_text(encoding="utf-8"))
        except ProfileError as error:
            self.workspace.show_notice(t.profile_error[error.reason], warning=True)
            return
        except (OSError, UnicodeDecodeError):
            self.workspace.show_notice(t.profile_error["invalid"], warning=True)
            return
        dataset = self.dataset
        run_in_background(
            lambda: run_profile(dataset, profile),
            lambda results: self._preview_profile(profile, results),
            lambda error: self.workspace.show_notice(t.profile_error["invalid"], warning=True),
        )

    def _preview_profile(self, profile, results) -> None:
        dialog = ProfileDialog(self._i18n, profile, results, self)
        if dialog.exec():
            self.apply_profile_results(profile, results)

    def apply_profile_results(self, profile, results) -> None:
        applied = 0
        for result in results:
            if result.status != "applied" or result.count == 0:
                continue
            step = result.step
            if step["type"] == "removeDuplicates":
                operation = RemoveRowsOperation("exact", result.count, result.filled)
            else:
                action = {"transform": step.get("transform"), "replace": "custom", "map": "similar"}.get(
                    step["type"], step["type"]
                )
                column = result.dataset.columns.index(step["column"])
                operation = CellsOperation(column, action, result.count)
            self.history = push_entry(self.history, HistoryStep(result.dataset, operation, step))
            applied += 1
        self._refresh()
        self.workspace.show_notice(self._i18n.t.profile_applied(profile.name, applied))

    def move_in_history(self, move) -> None:
        if not self.history or self.pages.currentWidget() is not self.workspace:
            return
        self.history = move(self.history)
        self._refresh(keep_column=True)
        self.workspace.show_notice(None)

    @property
    def has_changes(self) -> bool:
        if not self.history:
            return False
        original, current = self.history.entries[0].dataset, self.dataset
        return count_modified_cells(original, current) > 0 or len(current.rows) != len(original.rows)

    def confirm_discard(self) -> bool:
        if not self.has_changes:
            return True
        t = self._i18n.t
        answer = QMessageBox.question(self, t.confirm_discard_title, t.confirm_discard)
        return answer == QMessageBox.StandardButton.Yes

    def select_sheet(self, name: str) -> None:
        sheet = next((sheet for sheet in self.sheets or [] if sheet.sheet == name), None)
        if not sheet or not self.dataset:
            return
        if not self.confirm_discard():
            self.workspace.summary.sheet_combo.setCurrentText(self.dataset.sheet or "")
            return
        try:
            self._show_dataset(sheet_to_dataset(sheet, self.dataset.file_name))
        except EmptySheetError:
            self.workspace.summary.sheet_combo.setCurrentText(self.dataset.sheet or "")
            self.statusBar().showMessage(self._i18n.t.empty_sheet(name), 5000)

    def show_start(self) -> None:
        if not self.confirm_discard():
            return
        self.history = None
        self.sheets = None
        self.pages.setCurrentWidget(self.start_page)
