from PySide6.QtCore import QMimeData, QPointF, Qt, QUrl
from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QApplication

from .test_ui_workspace import load, wait_for_background


def drop(window, path):
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(path))])
    event = QDropEvent(
        QPointF(200, 200), Qt.DropAction.CopyAction, mime, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
    )
    window.dropEvent(event)
    wait_for_background()


def test_window_icon_is_the_web_favicon():
    assert not QApplication.instance().windowIcon().isNull()


def test_dropping_a_file_anywhere_opens_it(window, tmp_path):
    path = tmp_path / "a.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    assert window.acceptDrops()
    drop(window, path)
    assert window.dataset.rows == [["1", "2"]]


def test_dropping_a_bad_file_on_the_workspace_shows_a_warning(window, tmp_path):
    window._i18n.set_language("en")
    load(window, tmp_path, "a,b\n1,2\n")
    bad = tmp_path / "old.xls"
    bad.write_text("x")
    drop(window, bad)
    assert window.pages.currentWidget() is window.workspace
    assert ".xls" in window.workspace.notice.text()


def test_credit_links_to_the_portfolio_on_every_page(window, tmp_path):
    assert "Raúl Estévez" in window.credit.text()
    assert 'href="https://raulesteveza.github.io/"' in window.credit.text()
    assert window.credit.isVisible()
    path = tmp_path / "a.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    drop(window, path)
    assert window.credit.isVisible()


def test_credit_follows_the_language(window):
    window._i18n.set_language("es")
    assert window.credit.text().startswith("Desarrollado por ")
    window._i18n.set_language("en")
    assert window.credit.text().startswith("Developed by ")


def test_window_can_shrink(window):
    minimum = window.minimumSizeHint()
    assert minimum.height() < 400
