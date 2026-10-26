"""Screen shown once a file is loaded: summary, columns and the data table."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ..core.dataset import Dataset, column_label
from .flow_layout import FlowLayout
from .i18n import I18n
from .table_model import DatasetTableModel
from .transform_panel import TransformPanel

FORMAT_NAMES = {"xlsx": "Excel", "json": "JSON", "xml": "XML"}


class DatasetSummary(QFrame):
    import_another = Signal()
    undo = Signal()
    redo = Signal()
    find_duplicates = Signal()
    export = Signal()
    column_selected = Signal(int)
    sheet_selected = Signal(str)

    def __init__(self, i18n: I18n):
        super().__init__()
        self.setObjectName("card")
        self._i18n = i18n
        self._dataset: Dataset | None = None
        self._selected: int | None = None

        self.file_name = QLabel()
        self.file_name.setProperty("role", "heading")
        self.privacy = QLabel()
        self.privacy.setProperty("role", "privacyTag")
        self.stats = QLabel()
        self.stats.setProperty("role", "muted")
        self.import_button = QPushButton()
        self.import_button.clicked.connect(self.import_another)
        self.export_button = QPushButton()
        self.export_button.setProperty("primary", True)
        self.export_button.clicked.connect(self.export)
        self.duplicates_button = QPushButton()
        self.duplicates_button.clicked.connect(self.find_duplicates)
        self.undo_button = QPushButton()
        self.undo_button.clicked.connect(self.undo)
        self.redo_button = QPushButton()
        self.redo_button.clicked.connect(self.redo)
        self.modified = 0
        self.removed = 0

        self.sheet_label = QLabel()
        self.sheet_label.setProperty("role", "label")
        self.sheet_combo = QComboBox()
        self.sheet_combo.activated.connect(lambda index: self.sheet_selected.emit(self.sheet_combo.itemText(index)))
        self.columns_label = QLabel()
        self.columns_label.setProperty("role", "label")
        self.columns = FlowLayout(spacing=8)

        title = QHBoxLayout()
        title.setSpacing(12)
        title.addWidget(self.file_name)
        title.addWidget(self.privacy)
        title.addStretch()
        title.addWidget(self.undo_button)
        title.addWidget(self.redo_button)
        title.addWidget(self.duplicates_button)
        title.addWidget(self.import_button)
        title.addWidget(self.export_button)
        sheet_row = QHBoxLayout()
        sheet_row.addWidget(self.sheet_label)
        sheet_row.addWidget(self.sheet_combo)
        sheet_row.addStretch()
        self.sheet_row = QWidget()
        self.sheet_row.setProperty("transparent", True)
        sheet_row.setContentsMargins(0, 0, 0, 0)
        self.sheet_row.setLayout(sheet_row)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addLayout(title)
        layout.addWidget(self.stats)
        layout.addWidget(self.sheet_row)
        layout.addWidget(self.columns_label)
        layout.addLayout(self.columns)

    def set_dataset(self, dataset: Dataset, sheets: list[str] | None) -> None:
        self._dataset = dataset
        self.sheet_row.setVisible(bool(sheets) and len(sheets) > 1)
        self.sheet_combo.clear()
        if sheets:
            self.sheet_combo.addItems(sheets)
            self.sheet_combo.setCurrentText(dataset.sheet or "")
        self.columns.clear()
        self._buttons = []
        for index in range(len(dataset.columns)):
            button = QPushButton(column_label(dataset, index))
            button.setProperty("tag", True)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _=False, index=index: self.column_selected.emit(index))
            self.columns.addWidget(button)
            self._buttons.append(button)
        self.retranslate()

    def set_selected_column(self, column: int | None) -> None:
        self._selected = column
        for index, button in enumerate(self._buttons):
            button.setChecked(index == column)

    def retranslate(self) -> None:
        t = self._i18n.t
        self.privacy.setText(t.privacy_short)
        self.import_button.setText(t.import_another)
        self.undo_button.setText(t.undo)
        self.undo_button.setToolTip(f"{t.undo} (Ctrl/Cmd+Z)")
        self.redo_button.setText(t.redo)
        self.redo_button.setToolTip(f"{t.redo} (Ctrl/Cmd+Shift+Z)")
        self.duplicates_button.setText(t.find_duplicates)
        self.export_button.setText(t.export)
        self.sheet_label.setText(t.sheet.upper())
        self.columns_label.setText(t.detected_columns.upper())
        if self._dataset:
            dataset = self._dataset
            self.file_name.setText(dataset.file_name)
            source = dataset.encoding.upper() if dataset.format == "csv" else FORMAT_NAMES[dataset.format]
            stats = f"{t.row_count(len(dataset.rows))} · {t.column_count(len(dataset.columns))} · {source}"
            if self.modified:
                stats += f" · <span style='color:#3fb950'>{t.modified_cells(self.modified)}</span>"
            if self.removed:
                stats += f" · <span style='color:#3fb950'>{t.removed_rows(self.removed)}</span>"
            self.stats.setText(stats)


class WorkspacePage(QWidget):
    import_another = Signal()
    sheet_selected = Signal(str)
    undo = Signal()
    redo = Signal()
    find_duplicates = Signal()
    export = Signal()
    # Updated dataset, applied count, action id, profile step
    applied = Signal(object, int, str, object)

    def __init__(self, i18n: I18n):
        super().__init__()
        self._i18n = i18n
        self.summary = DatasetSummary(i18n)
        self.summary.import_another.connect(self.import_another)
        self.summary.sheet_selected.connect(self.sheet_selected)
        self.summary.column_selected.connect(self.select_column)
        self.summary.undo.connect(self.undo)
        self.summary.redo.connect(self.redo)
        self.summary.find_duplicates.connect(self.find_duplicates)
        self.summary.export.connect(self.export)

        self.panel = TransformPanel(i18n)
        self.panel.applied.connect(self.applied)
        self.panel.hide()
        self.notice = QLabel()
        self.notice.setProperty("role", "notice")
        self.notice.setWordWrap(True)
        self.notice.hide()

        self.model = DatasetTableModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.table.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setDefaultSectionSize(160)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.table.horizontalHeader().sectionClicked.connect(self.select_column)
        self.table.verticalHeader().setDefaultSectionSize(30)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 8, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(self.summary)
        layout.addWidget(self.notice)
        # Desktop layout: table on the left, cleaning panel on the right with the full height
        # (the web stacks them for phones). The divider can be dragged.
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.panel)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.panel.setMinimumWidth(440)
        layout.addWidget(self.splitter, stretch=1)
        i18n.changed.connect(self.retranslate)

    @property
    def selected_column(self) -> int | None:
        return self.model.selected_column

    def set_dataset(
        self,
        dataset: Dataset,
        sheets: list[str] | None = None,
        modified: int = 0,
        keep_column: bool = False,
        removed: int = 0,
    ) -> None:
        column = self.selected_column if keep_column else None
        self.summary.modified = modified
        self.summary.removed = removed
        self.summary.set_dataset(dataset, sheets)
        self.model.empty_text = self._i18n.t.empty_cell
        self.model.set_dataset(dataset)
        self.select_column(column)

    def set_history_state(self, can_undo: bool, can_redo: bool) -> None:
        self.summary.undo_button.setEnabled(can_undo)
        self.summary.redo_button.setEnabled(can_redo)

    def show_notice(self, text: str | None) -> None:
        self.notice.setText(text or "")
        self.notice.setVisible(bool(text))

    def select_column(self, column: int | None) -> None:
        self.model.set_selected_column(column)
        self.summary.set_selected_column(column)
        if column is not None and self.model.dataset is not None:
            self.panel.set_target(self.model.dataset, column)
            if not self.panel.isVisible():
                self.panel.show()
                total = self.splitter.width()
                self.splitter.setSizes([int(total * 0.58), total - int(total * 0.58)])
            self.show_notice(None)
        else:
            self.panel.hide()

    def retranslate(self) -> None:
        self.summary.retranslate()
        self.model.empty_text = self._i18n.t.empty_cell
        self.model.layoutChanged.emit()
