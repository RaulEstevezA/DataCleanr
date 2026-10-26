"""Panel to clean the selected column: pick a transformation, review original -> proposed, apply."""

from collections.abc import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
)

from ..core.dataset import Dataset, apply_column_changes, column_label, preview_column_changes
from ..core.transforms import TRANSFORMS
from .flow_layout import FlowLayout
from .i18n import I18n
from .preview_model import ACCEPT, ARROW, ORIGINAL, PROPOSED, ROW, PreviewModel
from .session import CellAction


class TransformPanel(QFrame):
    # Updated dataset, number of applied changes, action id and the step to save in a profile
    applied = Signal(object, int, str, object)
    # True while a preview is shown: the window gives the panel more room
    preview_shown = Signal(bool)

    def __init__(self, i18n: I18n):
        super().__init__()
        self.setObjectName("card")
        self._i18n = i18n
        self.dataset: Dataset | None = None
        self.column: int | None = None
        self.action: CellAction | None = None

        self.title = QLabel()
        self.title.setProperty("role", "heading")
        self.actions = FlowLayout(spacing=8)
        self.action_buttons: dict[str, QPushButton] = {}
        for action in TRANSFORMS:
            button = QPushButton()
            button.setCheckable(True)
            button.setProperty("option", True)
            button.clicked.connect(lambda _=False, action=action: self.select_action(action))
            self.actions.addWidget(button)
            self.action_buttons[action] = button

        self.info = QLabel()
        self.info.setProperty("role", "muted")
        self.info.setWordWrap(True)

        self.model = PreviewModel()
        self.preview = QTableView()
        self.preview.setModel(self.model)
        self.preview.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.preview.verticalHeader().hide()
        header = self.preview.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        for column, mode in (
            (ACCEPT, QHeaderView.ResizeMode.ResizeToContents),
            (ROW, QHeaderView.ResizeMode.ResizeToContents),
            (ORIGINAL, QHeaderView.ResizeMode.Stretch),
            (ARROW, QHeaderView.ResizeMode.ResizeToContents),
            (PROPOSED, QHeaderView.ResizeMode.Stretch),
        ):
            header.setSectionResizeMode(column, mode)
        self.preview.setMinimumHeight(160)
        self.model.dataChanged.connect(self._update_summary)

        self.accept_all = QCheckBox()
        self.accept_all.clicked.connect(lambda checked: self.model.set_all(checked))
        self.summary = QLabel()
        self.summary.setProperty("role", "muted")
        self.cancel_button = QPushButton()
        self.cancel_button.clicked.connect(self.reset)
        self.apply_button = QPushButton()
        self.apply_button.setProperty("primary", True)
        self.apply_button.clicked.connect(self.apply)
        footer = QHBoxLayout()
        footer.addWidget(self.accept_all)
        footer.addWidget(self.summary)
        footer.addStretch()
        footer.addWidget(self.cancel_button)
        footer.addWidget(self.apply_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addLayout(self.actions)
        layout.addWidget(self.info)
        layout.addWidget(self.preview, stretch=1)
        layout.addLayout(footer)
        # Keeps the content at the top when there is no preview
        layout.addStretch(0)
        self._layout = layout
        self._footer_widgets = (self.accept_all, self.summary, self.cancel_button, self.apply_button)

        i18n.changed.connect(self.retranslate)
        self.retranslate()
        self.reset()

    def set_target(self, dataset: Dataset, column: int) -> None:
        self.dataset = dataset
        self.column = column
        self.reset()
        self.retranslate()

    def transform_for(self, action: CellAction) -> Callable[[str], str] | None:
        return TRANSFORMS.get(action)

    def profile_step(self, action: CellAction) -> dict:
        return {"type": "transform", "column": self.dataset.columns[self.column], "transform": action}

    def select_action(self, action: CellAction) -> None:
        self.action = action
        for key, button in self.action_buttons.items():
            button.setChecked(key == action)
        self.refresh_preview()

    def refresh_preview(self) -> None:
        transform = self.transform_for(self.action) if self.action else None
        if transform is None or self.dataset is None or self.column is None:
            self.model.set_changes(self.dataset, []) if self.dataset else None
            self._set_preview_visible(False)
            return
        changes = preview_column_changes(self.dataset, self.column, transform)
        self.model.set_changes(self.dataset, changes)
        self._set_preview_visible(bool(changes))
        self.info.setText("" if changes else self._i18n.t.no_changes)
        self.info.setVisible(not changes)
        self._update_summary()

    def _set_preview_visible(self, visible: bool) -> None:
        self.preview.setVisible(visible)
        for widget in self._footer_widgets:
            widget.setVisible(visible)
        self._layout.setStretch(self._layout.count() - 1, 0 if visible else 1)
        self.preview_shown.emit(visible)

    def _update_summary(self) -> None:
        t = self._i18n.t
        accepted, total = len(self.model.accepted), len(self.model.changes)
        self.summary.setText(t.changes_selected(accepted, total))
        self.apply_button.setText(t.apply_changes(accepted))
        self.apply_button.setEnabled(accepted > 0)
        self.accept_all.setCheckState(
            Qt.CheckState.Checked
            if accepted == total
            else Qt.CheckState.Unchecked
            if accepted == 0
            else Qt.CheckState.PartiallyChecked
        )

    def apply(self) -> None:
        if not self.dataset or self.column is None or not self.action:
            return
        accepted = self.model.accepted
        updated = apply_column_changes(self.dataset, self.column, accepted)
        self.applied.emit(updated, len(accepted), self.action, self.profile_step(self.action))
        self.reset()

    def reset(self) -> None:
        self.action = None
        for button in self.action_buttons.values():
            button.setChecked(False)
        self.info.hide()
        self._set_preview_visible(False)

    def retranslate(self) -> None:
        t = self._i18n.t
        for action, button in self.action_buttons.items():
            button.setText(t.transform_names[action])
        self.model.headers = ("", "#", t.original, "", t.proposed)
        self.model.empty_text = t.empty_cell
        self.accept_all.setText(t.accept_all)
        self.cancel_button.setText(t.cancel)
        if self.dataset is not None and self.column is not None:
            self.title.setText(t.clean_column(column_label(self.dataset, self.column)))
        if self.action:
            self.refresh_preview()
