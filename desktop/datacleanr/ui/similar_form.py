"""Unify similar values: one card per group of variants; the user picks or types the final value."""

import json

from PySide6.QtCore import QSettings, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..core.similar import SimilarGroup, SimilarOptions, group_similar_values
from .background import run_in_background
from .i18n import I18n
from .preview_model import visible_text

# Hundreds of cards would make the panel sluggish; hidden groups keep their suggested value
MAX_VISIBLE_GROUPS = 200


class GroupCard(QFrame):
    changed = Signal()

    def __init__(self, i18n: I18n, group: SimilarGroup):
        super().__init__()
        self.setObjectName("groupCard")
        self.group = group
        cells = sum(variant.count for variant in group.variants)
        t = i18n.t
        self.included = QCheckBox(t.similar_group_summary(len(group.variants), cells))
        self.included.setChecked(True)
        self.included.toggled.connect(self._toggled)
        self._choices = QButtonGroup(self)
        self._radios: dict[str, QRadioButton] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)
        layout.addWidget(self.included)
        legend = QLabel(t.similar_choose_value)
        legend.setProperty("role", "muted")
        layout.addWidget(legend)
        for variant in group.variants:
            row = QHBoxLayout()
            radio = QRadioButton(visible_text(variant.value, ""))
            radio.setToolTip(variant.value)
            radio.setChecked(variant.value == group.suggested)
            radio.toggled.connect(lambda checked: checked and self.changed.emit())
            self._choices.addButton(radio)
            self._radios[variant.value] = radio
            count = QLabel(f"×{variant.count}")
            count.setProperty("role", "muted")
            row.addWidget(radio)
            row.addStretch()
            row.addWidget(count)
            layout.addLayout(row)
        other_row = QHBoxLayout()
        self.other = QRadioButton(t.similar_other)
        self.other.toggled.connect(lambda checked: checked and self.changed.emit())
        self._choices.addButton(self.other)
        self.custom = QLineEdit()
        self.custom.setPlaceholderText(t.replace_placeholder)
        self.custom.textEdited.connect(self._custom_edited)
        other_row.addWidget(self.other)
        other_row.addWidget(self.custom, stretch=1)
        layout.addLayout(other_row)
        self._body = [*self._radios.values(), self.other, self.custom, legend]

    def _toggled(self, included: bool) -> None:
        for widget in self._body:
            widget.setEnabled(included)
        self.changed.emit()

    def _custom_edited(self) -> None:
        if not self.other.isChecked():
            self.other.setChecked(True)  # emits changed
        else:
            self.changed.emit()

    @property
    def target(self) -> str | None:
        """Chosen value, or None when the group is excluded or the custom value is empty."""
        if not self.included.isChecked():
            return None
        if self.other.isChecked():
            return self.custom.text() or None
        return next(value for value, radio in self._radios.items() if radio.isChecked())


class SimilarForm(QWidget):
    changed = Signal()

    def __init__(self, i18n: I18n):
        super().__init__()
        self.setProperty("transparent", True)
        self._i18n = i18n
        self._settings = QSettings()
        try:
            stored = json.loads(self._settings.value("similarOptions") or "{}")
        except (TypeError, ValueError):
            stored = {}
        self.threshold = QSlider(Qt.Orientation.Horizontal)
        self.threshold.setRange(70, 100)
        self.threshold.setValue(int(stored.get("threshold", 85)))
        self.threshold_label = QLabel()
        self.threshold_label.setProperty("role", "muted")
        self.threshold_hint = QLabel()
        self.threshold_hint.setProperty("role", "muted")
        self.threshold_hint.setWordWrap(True)
        self.legal_forms = QCheckBox()
        self.legal_forms.setChecked(bool(stored.get("ignoreLegalForms", True)))
        self.status = QLabel()
        self.status.setProperty("role", "muted")
        self.status.setWordWrap(True)
        self.cards_box = QWidget()
        self.cards_box.setProperty("transparent", True)
        self.cards = QVBoxLayout(self.cards_box)
        self.cards.setContentsMargins(0, 0, 0, 0)
        self.cards.setSpacing(10)

        # Recompute shortly after the slider stops moving, not on every step
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self._options_changed)
        self.threshold.valueChanged.connect(self._threshold_moved)
        self.legal_forms.toggled.connect(self._options_changed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        for widget in (self.threshold_label, self.threshold, self.threshold_hint, self.legal_forms, self.status):
            layout.addWidget(widget)
        layout.addWidget(self.cards_box)

        self._values: list[str] = []
        self._groups: list[SimilarGroup] = []
        self._card_widgets: list[GroupCard] = []
        self._generation = 0
        i18n.changed.connect(self.retranslate)
        self.retranslate()

    @property
    def options(self) -> SimilarOptions:
        return SimilarOptions(self.threshold.value(), self.legal_forms.isChecked())

    def set_values(self, values: list[str]) -> None:
        self._values = values
        self._compute()

    def _threshold_moved(self) -> None:
        self.retranslate()
        self._debounce.start()

    def _options_changed(self) -> None:
        self._settings.setValue(
            "similarOptions",
            json.dumps({"threshold": self.threshold.value(), "ignoreLegalForms": self.legal_forms.isChecked()}),
        )
        self._compute()

    def _compute(self) -> None:
        # Results of an older computation are ignored if the options changed meanwhile
        self._generation += 1
        generation, values, options = self._generation, self._values, self.options
        self.status.setText(self._i18n.t.similar_searching)
        self.status.show()
        run_in_background(
            lambda: group_similar_values(values, options),
            lambda groups: generation == self._generation and self._show_groups(groups),
            lambda error: generation == self._generation and self.status.setText(str(error)),
        )

    def _show_groups(self, groups: list[SimilarGroup]) -> None:
        self._groups = groups
        for card in self._card_widgets:
            card.deleteLater()
        self._card_widgets = []
        for group in groups[:MAX_VISIBLE_GROUPS]:
            card = GroupCard(self._i18n, group)
            card.changed.connect(self.changed)
            self.cards.addWidget(card)
            self._card_widgets.append(card)
        t = self._i18n.t
        if not groups:
            self.status.setText(t.similar_none)
        elif len(groups) > MAX_VISIBLE_GROUPS:
            self.status.setText(t.similar_truncated(MAX_VISIBLE_GROUPS, len(groups)))
        else:
            self.status.hide()
        self.changed.emit()

    @property
    def ready(self) -> bool:
        return bool(self._groups) or self.status.text() == self._i18n.t.similar_none

    def mapping(self) -> dict[str, str]:
        """Variant -> chosen value, for the groups the user kept."""
        result: dict[str, str] = {}
        for index, group in enumerate(self._groups):
            target = self._card_widgets[index].target if index < len(self._card_widgets) else group.suggested
            if not target:
                continue
            for variant in group.variants:
                if variant.value != target:
                    result[variant.value] = target
        return result

    def retranslate(self) -> None:
        t = self._i18n.t
        self.threshold_label.setText(t.similar_threshold(self.threshold.value()))
        self.threshold_hint.setText(t.similar_threshold_hint)
        self.legal_forms.setText(t.similar_ignore_legal_forms)
