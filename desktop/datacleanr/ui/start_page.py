"""First screen: presentation card, privacy notice and the place to load a file."""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from .i18n import I18n

SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".json", ".xml")


def _label(role: str | None = None, wrap: bool = True) -> QLabel:
    label = QLabel()
    label.setWordWrap(wrap)
    if role:
        label.setProperty("role", role)
    return label


class DropZone(QFrame):
    """Dashed area that accepts a dropped file or opens a file dialog."""

    file_selected = Signal(Path)

    def __init__(self, i18n: I18n):
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self._i18n = i18n

        self.title = _label("heading")
        self.description = _label("muted")
        self.button = QPushButton()
        self.button.setProperty("primary", True)
        self.button.clicked.connect(self._choose_file)
        self.hint = _label("muted")
        self.error = _label("error")
        self.error.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 36, 24, 36)
        layout.setSpacing(12)
        for widget in (self.title, self.description):
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(widget)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        for widget in (self.hint, self.error):
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(widget)

    def retranslate(self) -> None:
        t = self._i18n.t
        self.title.setText(t.import_title)
        self.description.setText(t.import_description)
        self.button.setText(t.import_button)
        self.hint.setText(t.import_hint)

    def set_loading(self, loading: bool) -> None:
        self.button.setEnabled(not loading)
        self.button.setText(self._i18n.t.import_loading if loading else self._i18n.t.import_button)

    def show_error(self, message: str | None) -> None:
        self.error.setText(message or "")
        self.error.setVisible(bool(message))

    def _choose_file(self) -> None:
        patterns = " ".join(f"*{extension}" for extension in SUPPORTED_EXTENSIONS)
        path, _ = QFileDialog.getOpenFileName(
            self, self._i18n.t.import_button, "", f"CSV, Excel, JSON, XML ({patterns})"
        )
        if path:
            self.file_selected.emit(Path(path))

    def _set_dragging(self, dragging: bool) -> None:
        self.setProperty("dragging", dragging)
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event) -> None:  # noqa: N802 (Qt API name)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._set_dragging(True)

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self._set_dragging(False)

    def dropEvent(self, event) -> None:  # noqa: N802
        self._set_dragging(False)
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self.file_selected.emit(Path(urls[0].toLocalFile()))


class StartPage(QWidget):
    """Same structure as the web intro card: title, description, privacy callout and drop zone."""

    file_selected = Signal(Path)

    def __init__(self, i18n: I18n):
        super().__init__()
        self._i18n = i18n

        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(1000)

        self.title = _label("title")
        self.title.setText("DataCleanr")
        self.subtitle = _label("subtitle")
        self.description = _label("muted")

        callout = QFrame()
        callout.setObjectName("callout")
        callout_layout = QVBoxLayout(callout)
        callout_layout.setContentsMargins(20, 16, 20, 16)
        callout_layout.setSpacing(6)
        self.callout_title = _label("calloutTitle")
        callout_layout.addWidget(self.callout_title)
        self.callout_points = [_label() for _ in range(3)]
        for point in self.callout_points:
            callout_layout.addWidget(point)

        self.drop_zone = DropZone(i18n)
        self.drop_zone.file_selected.connect(self.file_selected)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 36)
        card_layout.setSpacing(16)
        for widget in (self.title, self.subtitle, self.description, callout, self.drop_zone):
            card_layout.addWidget(widget)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(card, stretch=100)
        row.addStretch()
        content = QWidget()
        content.setProperty("transparent", True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 8, 24, 24)
        content_layout.addLayout(row)
        content_layout.addStretch()
        # Scrolls on short windows instead of forcing a minimum window height
        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        i18n.changed.connect(self.retranslate)
        self.retranslate()

    def retranslate(self) -> None:
        t = self._i18n.t
        self.subtitle.setText(t.tagline)
        self.description.setText(t.intro_description)
        self.callout_title.setText(t.privacy_title)
        for label, text in zip(self.callout_points, t.privacy_points, strict=True):
            label.setText(f"•  {text}")
        self.drop_zone.retranslate()
