"""Preview of a cleaning profile: what each step would do before anything is applied."""

from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout

from ..core.profile import Profile, StepResult
from . import theme
from .i18n import I18n
from .labels import describe_profile_step


class ProfileDialog(QDialog):
    def __init__(self, i18n: I18n, profile: Profile, results: list[StepResult], parent=None):
        super().__init__(parent)
        t = i18n.t
        self.setWindowTitle(t.profile_title(profile.name))
        self.resize(720, 520)
        self.effective = [r for r in results if r.status == "applied" and r.count > 0]

        hint = QLabel(t.profile_apply_hint)
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)
        steps = QListWidget()
        for index, result in enumerate(results, start=1):
            if result.status == "skipped":
                outcome, color = t.profile_skipped, theme.WARNING
            elif result.step["type"] == "removeDuplicates":
                outcome, color = t.removed_rows(result.count), theme.SUCCESS if result.count else theme.MUTED
            else:
                outcome, color = t.modified_cells(result.count), theme.SUCCESS if result.count else theme.MUTED
            item = QListWidgetItem(f"{index}    {describe_profile_step(t, result.step)}    —    {outcome}")
            item.setForeground(QBrush(QColor(color)))
            steps.addItem(item)

        summary = QLabel(t.profile_summary(len(self.effective), len(results)))
        summary.setProperty("role", "muted")
        cancel = QPushButton(t.cancel)
        cancel.clicked.connect(self.reject)
        apply = QPushButton(t.profile_apply(len(self.effective)))
        apply.setProperty("primary", True)
        apply.setEnabled(bool(self.effective))
        apply.clicked.connect(self.accept)
        footer = QHBoxLayout()
        footer.addWidget(summary)
        footer.addStretch()
        footer.addWidget(cancel)
        footer.addWidget(apply)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addWidget(hint)
        layout.addWidget(steps, stretch=1)
        layout.addLayout(footer)
