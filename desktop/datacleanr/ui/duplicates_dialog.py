"""Find duplicate rows (exact or possible), choose the row to keep in each group and remove the rest."""

import json
from dataclasses import dataclass, replace

from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.dataset import Dataset, column_label, remove_rows, row_number
from ..core.duplicates import (
    DuplicateOptions,
    MergedRow,
    SimilarRowsOptions,
    find_duplicate_rows,
    find_similar_rows,
    merge_rows,
)
from . import theme
from .background import run_in_background
from .flow_layout import FlowLayout
from .i18n import I18n
from .preview_model import visible_text

# Rendering thousands of groups at once would make the window sluggish
MAX_VISIBLE_GROUPS = 100


@dataclass
class Group:
    rows: list[int]
    # Similarity to the group's first row; only for possible duplicates
    scores: list[float] | None = None


@dataclass(frozen=True)
class RemovalResult:
    dataset: Dataset
    removed: int
    filled: int
    mode: str
    # Replayable step for a profile; None for possible duplicates (they need a person to confirm)
    profile_step: dict | None


class GroupView(QFrame):
    """One group: include checkbox, table of rows with a "keep" radio, and the merged result."""

    def __init__(self, dialog: "DuplicatesDialog", index: int, group: Group):
        super().__init__()
        self.setObjectName("groupCard")
        self.dialog, self.index, self.group = dialog, index, group
        t = dialog.i18n.t
        dataset = dialog.dataset
        title = t.duplicates_similar_group(len(group.rows)) if group.scores else t.duplicates_group(len(group.rows))
        self.included = QCheckBox(title)
        # Exact duplicates are included by default; possible duplicates must be confirmed one by one
        self.included.setChecked(group.scores is None)
        self.included.toggled.connect(dialog.update_summary)

        extra = 3 if group.scores else 2
        self.table = QTableWidget(len(group.rows) + 1, extra + len(dataset.columns))
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        headers = [t.duplicates_keep, "#"] + ([t.duplicates_score] if group.scores else [])
        self.table.setHorizontalHeaderLabels(headers + [column_label(dataset, c) for c in range(len(dataset.columns))])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._keep = QButtonGroup(self)
        for position, row in enumerate(group.rows):
            radio = QRadioButton()
            radio.setChecked(position == 0)
            radio.toggled.connect(lambda checked: checked and dialog.update_summary())
            self._keep.addButton(radio, position)
            holder = QWidget()
            holder.setProperty("transparent", True)
            holder_layout = QHBoxLayout(holder)
            holder_layout.setContentsMargins(8, 0, 0, 0)
            holder_layout.addWidget(radio)
            self.table.setCellWidget(position, 0, holder)
            self.table.setItem(position, 1, QTableWidgetItem(str(row_number(dataset, row))))
            if group.scores:
                score = "—" if position == 0 else f"{int(group.scores[position])}%"
                self.table.setItem(position, 2, QTableWidgetItem(score))
            for c, cell in enumerate(dataset.rows[row]):
                self.table.setItem(position, extra + c, QTableWidgetItem(visible_text(cell, t.empty_cell)))
        self._result_row = len(group.rows)
        self.table.setItem(self._result_row, 1, QTableWidgetItem(t.duplicates_result))
        self.table.setFixedHeight(self.table.horizontalHeader().height() + 30 * (len(group.rows) + 1) + 4)
        for r in range(self.table.rowCount()):
            self.table.setRowHeight(r, 30)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.addWidget(self.included)
        layout.addWidget(self.table)

    @property
    def keep(self) -> int:
        return self.group.rows[max(self._keep.checkedId(), 0)]

    def merged(self) -> MergedRow:
        rows = [self.dialog.dataset.rows[r] for r in self.group.rows]
        return merge_rows(rows, self.group.rows.index(self.keep))

    def refresh(self, merge: bool) -> None:
        """Strikes the rows that will be removed and shows the merged result row."""
        included = self.included.isChecked()
        extra = 3 if self.group.scores else 2
        for position, row in enumerate(self.group.rows):
            removed = included and row != self.keep
            for c in range(1, self.table.columnCount()):
                item = self.table.item(position, c)
                if item:
                    font = item.font()
                    font.setStrikeOut(removed)
                    item.setFont(font)
                    item.setForeground(QBrush(QColor(theme.DANGER if removed else theme.TEXT)))
        merged = self.merged() if merge and included else None
        show_result = bool(merged and merged.filled)
        self.table.setRowHidden(self._result_row, not show_result)
        if show_result:
            for c, cell in enumerate(merged.row):
                item = QTableWidgetItem(visible_text(cell, ""))
                if c in merged.conflicts:
                    item.setForeground(QBrush(QColor(theme.WARNING)))
                    item.setToolTip(self.dialog.i18n.t.duplicates_conflict)
                elif c in merged.filled:
                    item.setForeground(QBrush(QColor(theme.SUCCESS)))
                self.table.setItem(self._result_row, extra + c, item)
        rows = len(self.group.rows) + (1 if show_result else 0)
        self.table.setFixedHeight(self.table.horizontalHeader().height() + 30 * rows + 4)


class DuplicatesDialog(QDialog):
    def __init__(self, i18n: I18n, dataset: Dataset, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.dataset = dataset
        self.result: RemovalResult | None = None
        t = i18n.t
        self.setWindowTitle(t.duplicates_title)
        self.resize(1100, 760)
        self._settings = QSettings()
        try:
            stored = json.loads(self._settings.value("similarRows") or "{}")
        except (TypeError, ValueError):
            stored = {}

        self.exact_button = QPushButton(t.duplicates_exact)
        self.similar_button = QPushButton(t.duplicates_similar)
        modes = QButtonGroup(self)
        for button in (self.exact_button, self.similar_button):
            button.setCheckable(True)
            button.setProperty("option", True)
            modes.addButton(button)
            button.clicked.connect(self._recompute)
        self.exact_button.setChecked(True)

        self.compare_label = QLabel()
        self.compare_label.setProperty("role", "muted")
        self.compare_label.setWordWrap(True)
        self.columns = FlowLayout(spacing=8)
        self.column_buttons = []
        for c in range(len(dataset.columns)):
            button = QPushButton(column_label(dataset, c))
            button.setProperty("tag", True)
            button.setCheckable(True)
            button.setChecked(True)
            button.clicked.connect(self._recompute)
            self.columns.addWidget(button)
            self.column_buttons.append(button)

        self.ignore_case = QCheckBox(t.duplicates_ignore_case)
        self.ignore_case.toggled.connect(self._recompute)
        self.threshold = QSlider(Qt.Orientation.Horizontal)
        self.threshold.setRange(70, 100)
        self.threshold.setValue(int(stored.get("threshold", 85)))
        self.threshold_label = QLabel()
        self.threshold_label.setProperty("role", "muted")
        self.legal_forms = QCheckBox(t.similar_ignore_legal_forms)
        self.legal_forms.setChecked(bool(stored.get("ignoreLegalForms", True)))
        self.legal_forms.toggled.connect(self._recompute)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self._recompute)
        self.threshold.valueChanged.connect(self._threshold_moved)
        self.merge = QCheckBox(t.duplicates_merge)
        self.merge.setChecked(self._settings.value("mergeDuplicates", "true") == "true")
        self.merge.toggled.connect(self._merge_toggled)
        self.hint = QLabel()
        self.hint.setProperty("role", "muted")
        self.hint.setWordWrap(True)
        self.status = QLabel()
        self.status.setProperty("role", "muted")

        self.groups_box = QWidget()
        self.groups_box.setProperty("transparent", True)
        self.groups_layout = QVBoxLayout(self.groups_box)
        self.groups_layout.setContentsMargins(0, 0, 0, 0)
        self.groups_layout.setSpacing(10)
        self.groups_layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidget(self.groups_box)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.summary = QLabel()
        self.summary.setProperty("role", "muted")
        self.cancel_button = QPushButton(t.cancel)
        self.cancel_button.clicked.connect(self.reject)
        self.remove_button = QPushButton()
        self.remove_button.setProperty("primary", True)
        self.remove_button.clicked.connect(self._remove)

        mode_row = QHBoxLayout()
        mode_row.addWidget(self.exact_button)
        mode_row.addWidget(self.similar_button)
        mode_row.addStretch()
        footer = QHBoxLayout()
        footer.addWidget(self.summary)
        footer.addStretch()
        footer.addWidget(self.cancel_button)
        footer.addWidget(self.remove_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addLayout(mode_row)
        layout.addWidget(self.compare_label)
        layout.addLayout(self.columns)
        for widget in (self.ignore_case, self.threshold_label, self.threshold, self.legal_forms, self.merge, self.hint):
            layout.addWidget(widget)
        layout.addWidget(self.status)
        layout.addWidget(scroll, stretch=1)
        layout.addLayout(footer)

        self._views: list[GroupView] = []
        self._groups: list[Group] = []
        self._generation = 0
        self._recompute()

    @property
    def mode(self) -> str:
        return "similar" if self.similar_button.isChecked() else "exact"

    def _selected_columns(self) -> list[int]:
        return [c for c, button in enumerate(self.column_buttons) if button.isChecked()]

    def _threshold_moved(self) -> None:
        self.threshold_label.setText(self.i18n.t.similar_threshold(self.threshold.value()))
        self._debounce.start()

    def _merge_toggled(self, merge: bool) -> None:
        self._settings.setValue("mergeDuplicates", "true" if merge else "false")
        self.update_summary()

    def _recompute(self) -> None:
        t = self.i18n.t
        similar = self.mode == "similar"
        self.ignore_case.setVisible(not similar)
        for widget in (self.threshold_label, self.threshold, self.legal_forms):
            widget.setVisible(similar)
        self.threshold_label.setText(t.similar_threshold(self.threshold.value()))
        self.compare_label.setText(t.duplicates_compare_similar if similar else t.duplicates_compare)
        self.hint.setText(t.duplicates_similar_hint if similar else t.duplicates_hint)
        if similar:
            self._settings.setValue(
                "similarRows",
                json.dumps({"threshold": self.threshold.value(), "ignoreLegalForms": self.legal_forms.isChecked()}),
            )

        columns, rows = self._selected_columns(), self.dataset.rows
        if similar:
            options = SimilarRowsOptions(columns, self.threshold.value(), self.legal_forms.isChecked())

            def work():
                return [Group(g.rows, g.scores) for g in find_similar_rows(rows, options)]
        else:
            exact = DuplicateOptions(columns, self.ignore_case.isChecked())

            def work():
                return [Group(group) for group in find_duplicate_rows(rows, exact)]

        # Results of an older search are ignored if the options changed meanwhile
        self._generation += 1
        generation = self._generation
        self.status.setText(t.duplicates_searching)
        self.status.show()
        run_in_background(
            work,
            lambda groups: generation == self._generation and self._show_groups(groups),
            lambda error: generation == self._generation and self.status.setText(str(error)),
        )

    def _show_groups(self, groups: list[Group]) -> None:
        t = self.i18n.t
        self._groups = groups
        for view in self._views:
            view.deleteLater()
        self._views = []
        for index, group in enumerate(groups[:MAX_VISIBLE_GROUPS]):
            view = GroupView(self, index, group)
            self.groups_layout.insertWidget(self.groups_layout.count() - 1, view)
            self._views.append(view)
        if not self._selected_columns():
            self.status.setText(t.duplicates_no_columns)
        elif not groups:
            self.status.setText(t.duplicates_none)
        elif len(groups) > MAX_VISIBLE_GROUPS:
            self.status.setText(t.duplicates_truncated(MAX_VISIBLE_GROUPS, len(groups)))
        else:
            self.status.hide()
        self.update_summary()

    def _plans(self) -> list[tuple[int, list[int], MergedRow | None]]:
        """(kept row, removed rows, merged row) for every included group."""
        merge = self.merge.isChecked()
        plans = []
        for index, group in enumerate(self._groups):
            if index < len(self._views):
                view = self._views[index]
                if not view.included.isChecked():
                    continue
                keep, merged = view.keep, view.merged() if merge else None
            elif group.scores is None:
                # Hidden exact groups keep their first row; hidden possible groups are left alone
                keep = group.rows[0]
                merged = merge_rows([self.dataset.rows[r] for r in group.rows], 0) if merge else None
            else:
                continue
            plans.append((keep, [r for r in group.rows if r != keep], merged))
        return plans

    def update_summary(self) -> None:
        t = self.i18n.t
        merge = self.merge.isChecked()
        for view in self._views:
            view.refresh(merge)
        plans = self._plans()
        removed = sum(len(remove) for _, remove, _ in plans)
        filled = sum(len(merged.filled) for _, _, merged in plans if merged)
        summary = t.duplicates_summary(len(self._groups), removed)
        if filled:
            summary += f" · {t.duplicates_filled(filled)}"
        self.summary.setText(summary)
        self.remove_button.setText(t.duplicates_remove(removed))
        self.remove_button.setEnabled(removed > 0)

    def _remove(self) -> None:
        plans = self._plans()
        rows = list(self.dataset.rows)
        for keep, _, merged in plans:
            if merged:
                rows[keep] = merged.row
        indexes = {row for _, remove, _ in plans for row in remove}
        filled = sum(len(merged.filled) for _, _, merged in plans if merged)
        updated = remove_rows(replace(self.dataset, rows=rows), indexes)
        step = (
            {
                "type": "removeDuplicates",
                "columns": [self.dataset.columns[c] for c in self._selected_columns()],
                "ignoreCaseAndSpaces": self.ignore_case.isChecked(),
                "merge": self.merge.isChecked(),
            }
            if self.mode == "exact"
            else None
        )
        self.result = RemovalResult(updated, len(indexes), filled, self.mode, step)
        self.accept()
