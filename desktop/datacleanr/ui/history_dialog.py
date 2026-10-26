"""History of applied steps: go back to any of them, or save them as a cleaning profile."""

import re
import unicodedata
from pathlib import Path

from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from ..core.history import History
from ..core.profile import Profile, serialize_profile
from . import theme
from .i18n import I18n
from .labels import describe_step
from .session import HistoryStep


def profile_file_name(name: str) -> str:
    """ "Clientes mensuales" -> "clientes-mensuales.datacleanr.json" (same as the web version)."""
    plain = "".join(c for c in unicodedata.normalize("NFD", name) if not unicodedata.category(c).startswith("M"))
    slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    return f"{slug or 'profile'}.datacleanr.json"


class HistoryDialog(QDialog):
    def __init__(self, i18n: I18n, history: History[HistoryStep], parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.history = history
        # Index chosen by the user to go back (or forward) to; None if unchanged
        self.go_to_index: int | None = None
        self.saved_path: Path | None = None
        t = i18n.t
        self.setWindowTitle(t.history_title(len(history.entries) - 1))
        self.resize(640, 560)

        self.steps = QListWidget()
        for index, step in enumerate(history.entries):
            item = QListWidgetItem(f"{index}    {describe_step(t, step)}")
            if index == history.index:
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QBrush(QColor(theme.ACCENT_TEXT)))
            elif index > history.index:
                font = QFont()
                font.setStrikeOut(True)
                item.setFont(font)
                item.setForeground(QBrush(QColor(theme.MUTED)))
            self.steps.addItem(item)
        self.steps.setCurrentRow(history.index)
        self.steps.itemDoubleClicked.connect(lambda _item: self._go_to())
        hint = QLabel(t.history_hint)
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)
        self.go_button = QPushButton(t.history_go_to)
        self.go_button.clicked.connect(self._go_to)

        # Only the steps up to the current one (undone steps are not part of the result)
        applied = history.entries[1 : history.index + 1]
        self.replayable = [step.profile_step for step in applied if step.profile_step]
        not_replayable = len(applied) - len(self.replayable)
        self.name = QLineEdit()
        self.name.setPlaceholderText(t.profile_default_name)
        name_label = QLabel(t.profile_save_label)
        name_label.setProperty("role", "muted")
        self.save_button = QPushButton(t.profile_save(len(self.replayable)))
        self.save_button.setEnabled(bool(self.replayable))
        self.save_button.clicked.connect(self._save_profile)
        save_hint = QLabel(t.profile_save_hint)
        save_hint.setProperty("role", "muted")
        save_hint.setWordWrap(True)
        warning = QLabel(t.profile_not_replayable(not_replayable))
        warning.setProperty("role", "muted")
        warning.setWordWrap(True)
        warning.setVisible(not_replayable > 0)

        go_row = QHBoxLayout()
        go_row.addWidget(hint, stretch=1)
        go_row.addWidget(self.go_button)
        save_row = QHBoxLayout()
        save_row.addWidget(self.name, stretch=1)
        save_row.addWidget(self.save_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addWidget(self.steps, stretch=1)
        layout.addLayout(go_row)
        layout.addSpacing(8)
        layout.addWidget(name_label)
        layout.addLayout(save_row)
        layout.addWidget(warning)
        layout.addWidget(save_hint)

    def _go_to(self) -> None:
        self.go_to_index = self.steps.currentRow()
        self.accept()

    def profile(self) -> Profile:
        name = self.name.text().strip() or self.i18n.t.profile_default_name
        return Profile(name, list(self.replayable))

    def _save_profile(self) -> None:
        profile = self.profile()
        path, _ = QFileDialog.getSaveFileName(
            self, self.i18n.t.profile_save(len(profile.steps)), profile_file_name(profile.name), "JSON (*.json)"
        )
        if path:
            Path(path).write_text(serialize_profile(profile), encoding="utf-8")
            self.saved_path = Path(path)
