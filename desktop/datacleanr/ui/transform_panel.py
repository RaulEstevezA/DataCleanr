"""Panel to clean the selected column: pick a transformation, review original -> proposed, apply."""

from collections.abc import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ..core.amount import normalize_amount
from ..core.dataset import Dataset, apply_column_changes, column_label, preview_column_changes, row_number
from ..core.date import normalize_date
from ..core.phone import normalize_phone
from ..core.replace import create_replace_transform
from ..core.transforms import TRANSFORMS
from .i18n import I18n
from .option_forms import AmountForm, DateForm, IssuesBox, PhoneForm, ReplaceForm
from .preview_model import ACCEPT, ARROW, ORIGINAL, PROPOSED, ROW, PreviewModel
from .session import CellAction


class TransformPanel(QFrame):
    # Updated dataset, number of applied changes, action id and the step to save in a profile
    applied = Signal(object, int, str, object)

    def __init__(self, i18n: I18n):
        super().__init__()
        self.setObjectName("card")
        self._i18n = i18n
        self.dataset: Dataset | None = None
        self.column: int | None = None
        self.action: CellAction | None = None

        self.title = QLabel()
        self.title.setProperty("role", "heading")
        # A dropdown instead of the web's buttons: it takes one line in the narrow side panel
        self.action_ids: list[CellAction] = [*TRANSFORMS, "custom", "phone", "date", "amount"]
        self.action_label = QLabel()
        self.action_label.setProperty("role", "muted")
        self.action_combo = QComboBox()
        self.action_combo.activated.connect(lambda index: self.select_action(self.action_combo.itemData(index)))

        self.forms = {
            "custom": ReplaceForm(i18n),
            "phone": PhoneForm(i18n),
            "date": DateForm(i18n),
            "amount": AmountForm(i18n),
        }
        # Only the current form is shown, so the panel takes the height of that form alone,
        # and forms never shrink below their natural height (the preview gives way instead)
        for form in self.forms.values():
            form.changed.connect(self.refresh_preview)
            form.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            form.hide()
        self.issues = IssuesBox(i18n)
        self.currency_warning = QLabel()
        self.currency_warning.setProperty("role", "warning")
        self.currency_warning.setWordWrap(True)

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
        # Two lines: the panel is narrow, and the buttons must never be cut
        selection = QHBoxLayout()
        selection.setSpacing(12)
        selection.addWidget(self.accept_all)
        selection.addWidget(self.summary)
        selection.addStretch()
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.apply_button)
        footer = QVBoxLayout()
        footer.addLayout(selection)
        footer.addLayout(buttons)

        content = QWidget()
        content.setProperty("transparent", True)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 8)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addWidget(self.action_label)
        layout.addWidget(self.action_combo)
        for form in self.forms.values():
            layout.addWidget(form)
        layout.addWidget(self.currency_warning)
        layout.addWidget(self.issues)
        layout.addWidget(self.info)
        layout.addWidget(self.preview, stretch=1)
        # Keeps the content at the top when there is no preview
        layout.addStretch(0)
        self._layout = layout

        # If the panel is short, its content scrolls; the footer with Apply always stays visible
        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setProperty("transparent", True)
        scroll.viewport().setProperty("transparent", True)
        self._scroll = scroll
        footer.setContentsMargins(24, 8, 24, 16)
        footer.setSpacing(10)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll, stretch=1)
        outer.addLayout(footer)
        self._footer_widgets = (self.accept_all, self.summary, self.cancel_button, self.apply_button)

        i18n.changed.connect(self.retranslate)
        self.retranslate()
        self.reset()

    def set_target(self, dataset: Dataset, column: int) -> None:
        self.dataset = dataset
        self.column = column
        self.forms["custom"].set_column_values([row[column] for row in dataset.rows])
        self.reset()
        self.retranslate()

    def normalizer_for(self, action: CellAction):
        """Normalizers report values they cannot handle (status "invalid"), which are left unchanged."""
        if action == "phone":
            options = self.forms["phone"].options
            return lambda value: normalize_phone(value, options)
        if action == "date":
            options = self.forms["date"].options
            return lambda value: normalize_date(value, options)
        if action == "amount":
            options = self.forms["amount"].options
            return lambda value: normalize_amount(value, options)
        return None

    def transform_for(self, action: CellAction) -> Callable[[str], str] | None:
        if normalize := self.normalizer_for(action):
            return lambda value: normalize(value).value
        if action == "custom":
            form = self.forms["custom"]
            return create_replace_transform(form.options) if form.has_search else None
        return TRANSFORMS.get(action)

    def profile_step(self, action: CellAction) -> dict:
        column = self.dataset.columns[self.column]
        if action == "custom":
            o = self.forms["custom"].options
            return {
                "type": "replace",
                "column": column,
                "find": o.find,
                "replacement": o.replacement,
                "wholeCell": o.whole_cell,
                "ignoreCase": o.ignore_case,
            }
        if action == "phone":
            o = self.forms["phone"].options
            return {"type": "phone", "column": column, "defaultCountry": o.default_country, "format": o.format}
        if action == "date":
            o = self.forms["date"].options
            return {
                "type": "date",
                "column": column,
                "inputOrder": o.input_order,
                "format": o.format,
                "twoDigitYearLimit": o.two_digit_year_limit,
            }
        if action == "amount":
            o = self.forms["amount"].options
            return {
                "type": "amount",
                "column": column,
                "ambiguousDecimal": o.ambiguous_decimal,
                "format": o.format,
                "twoDecimals": o.two_decimals,
            }
        return {"type": "transform", "column": column, "transform": action}

    def _update_warnings(self) -> None:
        normalize = self.normalizer_for(self.action) if self.action else None
        if not normalize or self.dataset is None:
            self.issues.set_issues([])
            self.currency_warning.hide()
            return
        issues, currencies = [], set()
        for index, row in enumerate(self.dataset.rows):
            result = normalize(row[self.column])
            if result.status == "invalid":
                issues.append((row_number(self.dataset, index), row[self.column]))
            if getattr(result, "currency", None):
                currencies.add(result.currency)
        self.issues.set_issues(issues)
        # Removing currency symbols from a column that mixes currencies would lose information
        self.currency_warning.setText(self._i18n.t.amount_mixed_currencies(", ".join(sorted(currencies))))
        self.currency_warning.setVisible(len(currencies) > 1)

    def select_action(self, action: CellAction) -> None:
        self.action = action
        self.action_combo.setCurrentIndex(self.action_combo.findData(action))
        for key, form in self.forms.items():
            form.setVisible(key == action)
        self.refresh_preview()

    def refresh_preview(self) -> None:
        transform = self.transform_for(self.action) if self.action else None
        self._update_warnings()
        if transform is None or self.dataset is None or self.column is None:
            if self.dataset:
                self.model.set_changes(self.dataset, [])
            self._set_preview_visible(False)
            self.info.hide()
            return
        changes = preview_column_changes(self.dataset, self.column, transform)
        self.model.set_changes(self.dataset, changes)
        self._set_preview_visible(bool(changes))
        t = self._i18n.t
        self.info.setText("" if changes else t.no_matches if self.action == "custom" else t.no_changes)
        self.info.setVisible(not changes)
        self._update_summary()

    def _set_preview_visible(self, visible: bool) -> None:
        self.preview.setVisible(visible)
        for widget in self._footer_widgets:
            widget.setVisible(visible)
        self._layout.setStretch(self._layout.count() - 1, 0 if visible else 1)

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
        self.action_combo.setCurrentIndex(-1)
        self.forms["custom"].reset()
        for form in self.forms.values():
            form.hide()
        self.issues.set_issues([])
        self.currency_warning.hide()
        self.info.hide()
        self._set_preview_visible(False)

    def retranslate(self) -> None:
        t = self._i18n.t
        self.action_label.setText(t.transformation)
        self.action_combo.blockSignals(True)
        self.action_combo.clear()
        for action in self.action_ids:
            self.action_combo.addItem(t.transform_names[action], action)
        self.action_combo.setPlaceholderText(t.choose_transformation)
        self.action_combo.setCurrentIndex(self.action_combo.findData(self.action) if self.action else -1)
        self.action_combo.blockSignals(False)
        self.model.headers = ("", "#", t.original, "", t.proposed)
        self.model.empty_text = t.empty_cell
        self.accept_all.setText(t.accept_all)
        self.cancel_button.setText(t.cancel)
        if self.dataset is not None and self.column is not None:
            self.title.setText(t.clean_column(column_label(self.dataset, self.column)))
        if self.action:
            self.refresh_preview()
