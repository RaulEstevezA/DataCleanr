"""Options for each normalization, remembered between sessions like in the web version."""

import json

import phonenumbers
from phonenumbers.geodata.locale import LOCALE_DATA
from PySide6.QtCore import QLocale, QSettings, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QCompleter,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..core.amount import AmountOptions
from ..core.date import DEFAULT_TWO_DIGIT_YEAR_LIMIT, DateOptions
from ..core.phone import PhoneOptions
from ..core.replace import ReplaceOptions
from .i18n import I18n


def _transparent(widget: QWidget) -> QWidget:
    widget.setProperty("transparent", True)
    return widget


def _muted(text: str = "") -> QLabel:
    label = QLabel(text)
    label.setProperty("role", "muted")
    label.setWordWrap(True)
    return label


def _columns(*groups: list[QWidget]) -> QVBoxLayout:
    """Groups of widgets stacked in one column (the panel sits beside the table), with space between groups."""
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    for index, widgets in enumerate(groups):
        if index:
            layout.addSpacing(10)
        for widget in widgets:
            layout.addWidget(widget)
    return layout


class _StoredOptions:
    """Reads and writes a form's options as JSON in QSettings; missing fields use the defaults."""

    def __init__(self, key: str, defaults: dict):
        self._settings = QSettings()
        self._key = key
        stored = self._settings.value(key)
        try:
            loaded = json.loads(stored) if stored else {}
        except (TypeError, ValueError):
            loaded = {}
        self.values = {**defaults, **{k: v for k, v in loaded.items() if k in defaults}}

    def save(self) -> None:
        self._settings.setValue(self._key, json.dumps(self.values))


class _RadioGroup(QWidget):
    """Vertical list of options with an example next to each, like the web forms."""

    changed = Signal(str)

    def __init__(self, options: list[tuple[str, str]]):
        super().__init__()
        _transparent(self)
        self.legend = _muted()
        self._group = QButtonGroup(self)
        self._buttons: dict[str, QRadioButton] = {}
        self._examples = dict(options)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.legend)
        for key, _ in options:
            button = QRadioButton()
            button.toggled.connect(lambda checked, key=key: checked and self.changed.emit(key))
            self._group.addButton(button)
            self._buttons[key] = button
            layout.addWidget(button)

    def set_value(self, key: str) -> None:
        self._buttons[key].setChecked(True)

    def set_texts(self, legend: str, names: dict[str, str]) -> None:
        self.legend.setText(legend)
        for key, button in self._buttons.items():
            example = self._examples[key]
            button.setText(f"{names[key]}   {example}" if example else names[key])


class ReplaceForm(QWidget):
    changed = Signal()

    def __init__(self, i18n: I18n):
        super().__init__()
        _transparent(self)
        self._i18n = i18n
        self.find = QLineEdit()
        self.replacement = QLineEdit()
        self.whole_cell = QCheckBox()
        self.whole_cell.setChecked(True)
        self.ignore_case = QCheckBox()
        self.ignore_case.setChecked(True)
        self.find_label, self.replace_label = _muted(), _muted()
        for widget in (self.find, self.replacement):
            widget.textChanged.connect(self.changed)
        for widget in (self.whole_cell, self.ignore_case):
            widget.toggled.connect(self.changed)
        self.setLayout(
            _columns(
                [self.find_label, self.find],
                [self.replace_label, self.replacement],
                [self.whole_cell, self.ignore_case],
            )
        )
        i18n.changed.connect(self.retranslate)
        self.retranslate()

    def set_column_values(self, values: list[str]) -> None:
        """Distinct values of the column, offered as suggestions while typing."""
        completer = QCompleter(sorted({v.strip() for v in values if v.strip()}), self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.find.setCompleter(completer)

    def reset(self) -> None:
        self.find.clear()
        self.replacement.clear()

    @property
    def options(self) -> ReplaceOptions:
        return ReplaceOptions(
            self.find.text(), self.replacement.text(), self.whole_cell.isChecked(), self.ignore_case.isChecked()
        )

    @property
    def has_search(self) -> bool:
        return self.find.text().strip() != ""

    def retranslate(self) -> None:
        t = self._i18n.t
        self.find_label.setText(t.find_label)
        self.replace_label.setText(t.replace_label)
        self.find.setPlaceholderText(t.find_placeholder)
        self.replacement.setPlaceholderText(t.replace_placeholder)
        self.whole_cell.setText(t.whole_cell)
        self.ignore_case.setText(t.ignore_case)


def country_name(code: str, language: str) -> str:
    """Spanish names come from the phonenumbers data ("*xx" entries point to another language's
    name); English names, and the few regions without data, come from Qt."""
    name = LOCALE_DATA.get(code, {}).get("es") if language == "es" else None
    for _ in range(5):
        if not name or not name.startswith("*"):
            break
        name = LOCALE_DATA[code].get(name[1:])
    if not name:
        name = QLocale.territoryToString(QLocale.codeToTerritory(code))
    return f"{name} ({code})" if name else code


def _default_country() -> str:
    territory = QLocale.territoryToCode(QLocale.system().territory())
    return territory if territory in phonenumbers.SUPPORTED_REGIONS else "ES"


class PhoneForm(QWidget):
    changed = Signal()

    def __init__(self, i18n: I18n):
        super().__init__()
        _transparent(self)
        self._i18n = i18n
        self._stored = _StoredOptions("phoneOptions", {"defaultCountry": _default_country(), "format": "E164"})
        self.country_label = _muted()
        self.country = QComboBox()
        self.country.currentIndexChanged.connect(self._country_changed)
        self.format = _RadioGroup(
            [("E164", "+34600123456"), ("INTERNATIONAL", "+34 600 12 34 56"), ("NATIONAL", "600 12 34 56")]
        )
        self.format.set_value(self._stored.values["format"])
        self.format.changed.connect(lambda value: self._update("format", value))
        self.hint = _muted()
        self.setLayout(_columns([self.country_label, self.country], [self.format], [self.hint]))
        i18n.changed.connect(self.retranslate)
        self.retranslate()

    def _country_changed(self) -> None:
        code = self.country.currentData()
        if code:
            self._update("defaultCountry", code)

    def _update(self, key: str, value) -> None:
        if self._stored.values.get(key) == value:
            return
        self._stored.values[key] = value
        self._stored.save()
        self.changed.emit()

    @property
    def options(self) -> PhoneOptions:
        return PhoneOptions(self._stored.values["defaultCountry"], self._stored.values["format"])

    def retranslate(self) -> None:
        t = self._i18n.t
        self.country_label.setText(t.phone_country)
        self.format.set_texts(t.phone_format, t.phone_format_names)
        self.hint.setText(t.phone_hint)
        language = self._i18n.language
        entries = sorted(
            ((country_name(code, language), code) for code in phonenumbers.SUPPORTED_REGIONS), key=lambda e: e[0]
        )
        self.country.blockSignals(True)
        self.country.clear()
        for name, code in entries:
            self.country.addItem(name, code)
        self.country.setCurrentIndex(self.country.findData(self._stored.values["defaultCountry"]))
        self.country.blockSignals(False)


class DateForm(QWidget):
    changed = Signal()

    def __init__(self, i18n: I18n):
        super().__init__()
        _transparent(self)
        self._i18n = i18n
        us = QLocale.system().name() == "en_US"
        self._stored = _StoredOptions(
            "dateOptions",
            {"inputOrder": "MDY" if us else "DMY", "format": "ISO", "twoDigitYearLimit": DEFAULT_TWO_DIGIT_YEAR_LIMIT},
        )
        self.order = _RadioGroup([("DMY", "13/07/2024"), ("MDY", "07/13/2024")])
        self.order.set_value(self._stored.values["inputOrder"])
        self.order.changed.connect(lambda value: self._update("inputOrder", value))
        self.format = _RadioGroup([("ISO", "2024-07-13"), ("DMY", "13/07/2024"), ("MDY", "07/13/2024")])
        self.format.set_value(self._stored.values["format"])
        self.format.changed.connect(lambda value: self._update("format", value))
        self.limit_label = _muted()
        self.limit = QSpinBox()
        self.limit.setRange(0, 99)
        self.limit.setMaximumWidth(90)
        self.limit.setValue(self._stored.values["twoDigitYearLimit"])
        self.limit.valueChanged.connect(lambda value: self._update("twoDigitYearLimit", value))
        self.limit_explanation = _muted()
        self.hint = _muted()
        self.setLayout(
            _columns(
                [self.order, self.limit_label, self.limit, self.limit_explanation],
                [self.format],
                [self.hint],
            )
        )
        i18n.changed.connect(self.retranslate)
        self.retranslate()

    def _update(self, key: str, value) -> None:
        if self._stored.values.get(key) == value:
            return
        self._stored.values[key] = value
        self._stored.save()
        self._explain_limit()
        self.changed.emit()

    def _explain_limit(self) -> None:
        limit = self._stored.values["twoDigitYearLimit"]
        if limit == 99:
            self.limit_explanation.setText("00–99 → 2000–2099")
        else:
            self.limit_explanation.setText(
                f"00–{limit:02d} → 2000–20{limit:02d} · {limit + 1:02d}–99 → 19{limit + 1:02d}–1999"
            )

    @property
    def options(self) -> DateOptions:
        values = self._stored.values
        return DateOptions(values["inputOrder"], values["format"], values["twoDigitYearLimit"])

    def retranslate(self) -> None:
        t = self._i18n.t
        self.order.set_texts(t.date_input_order, t.date_order_names)
        self.format.set_texts(t.date_format, t.date_format_names)
        self.limit_label.setText(t.date_two_digit_limit)
        self.hint.setText(t.date_hint)
        self._explain_limit()


class AmountForm(QWidget):
    changed = Signal()

    def __init__(self, i18n: I18n):
        super().__init__()
        _transparent(self)
        self._i18n = i18n
        english = QLocale.system().name().startswith("en")
        self._stored = _StoredOptions(
            "amountOptions", {"ambiguousDecimal": "." if english else ",", "format": "DOT", "twoDecimals": False}
        )
        self.separator = _RadioGroup([(",", "1.234 → 1234"), (".", "1.234 → 1.234")])
        self.separator.set_value(self._stored.values["ambiguousDecimal"])
        self.separator.changed.connect(lambda value: self._update("ambiguousDecimal", value))
        self.format = _RadioGroup(
            [
                ("DOT", "1234567.89"),
                ("COMMA", "1234567,89"),
                ("COMMA_GROUPED", "1.234.567,89"),
                ("DOT_GROUPED", "1,234,567.89"),
            ]
        )
        self.format.set_value(self._stored.values["format"])
        self.format.changed.connect(lambda value: self._update("format", value))
        self.two_decimals = QCheckBox()
        self.two_decimals.setChecked(self._stored.values["twoDecimals"])
        self.two_decimals.toggled.connect(lambda value: self._update("twoDecimals", value))
        self.hint = _muted()
        self.setLayout(_columns([self.separator, self.two_decimals], [self.format], [self.hint]))
        i18n.changed.connect(self.retranslate)
        self.retranslate()

    def _update(self, key: str, value) -> None:
        if self._stored.values.get(key) == value:
            return
        self._stored.values[key] = value
        self._stored.save()
        self.changed.emit()

    @property
    def options(self) -> AmountOptions:
        values = self._stored.values
        return AmountOptions(values["ambiguousDecimal"], values["format"], values["twoDecimals"])

    def retranslate(self) -> None:
        t = self._i18n.t
        self.separator.set_texts(t.amount_ambiguous, t.amount_separator_names)
        self.format.set_texts(t.amount_format, t.amount_format_names)
        self.two_decimals.setText(t.amount_two_decimals)
        self.hint.setText(t.amount_hint)


class IssuesBox(QWidget):
    """Warning with the values that could not be normalized; the list unfolds on demand."""

    def __init__(self, i18n: I18n):
        super().__init__()
        self.setProperty("role", "warningBox")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._i18n = i18n
        self.message = QLabel()
        self.message.setProperty("role", "warningText")
        self.message.setWordWrap(True)
        self.toggle = QPushButton()
        self.toggle.setProperty("warningToggle", True)
        self.toggle.setCheckable(True)
        self.toggle.toggled.connect(self._toggle)
        self.list = QListWidget()
        self.list.setMaximumHeight(160)
        self.list.hide()
        self._count = 0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        layout.addWidget(self.message)
        layout.addWidget(self.toggle, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.list)
        i18n.changed.connect(self.retranslate)

    def set_issues(self, issues: list[tuple[int, str]]) -> None:
        self._count = len(issues)
        self.list.clear()
        for row, value in issues:
            self.list.addItem(f"{row}    {value}")
        self.setVisible(bool(issues))
        self.retranslate()

    def _toggle(self, shown: bool) -> None:
        self.list.setVisible(shown)
        self.retranslate()

    def retranslate(self) -> None:
        t = self._i18n.t
        self.message.setText(t.normalize_issues(self._count))
        self.toggle.setText(t.hide_values if self.toggle.isChecked() else t.show_values)
