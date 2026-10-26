"""Main window: header with the language switcher and the current page."""

from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .i18n import MESSAGES, I18n
from .start_page import StartPage


class LanguageSwitcher(QWidget):
    def __init__(self, i18n: I18n):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        group = QButtonGroup(self)
        for code in MESSAGES:
            button = QPushButton(code.upper())
            button.setProperty("lang", True)
            button.setCheckable(True)
            button.setChecked(code == i18n.language)
            button.clicked.connect(lambda _=False, code=code: i18n.set_language(code))
            group.addButton(button)
            layout.addWidget(button)


class MainWindow(QMainWindow):
    def __init__(self, i18n: I18n):
        super().__init__()
        self._i18n = i18n
        self.setWindowTitle("DataCleanr")
        self.resize(1200, 820)

        header = QHBoxLayout()
        header.setContentsMargins(24, 16, 24, 8)
        brand = QLabel("DataCleanr")
        brand.setStyleSheet("font-weight: 600;")
        header.addWidget(brand)
        header.addStretch()
        header.addWidget(LanguageSwitcher(i18n))

        self.start_page = StartPage(i18n)
        self.start_page.file_selected.connect(self.open_file)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.start_page)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.pages)
        self.setCentralWidget(central)

    def open_file(self, path: Path) -> None:
        # Loading files comes in the next step
        self.statusBar().showMessage(str(path))
