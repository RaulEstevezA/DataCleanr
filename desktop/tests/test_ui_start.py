def test_start_page_switches_language(window):
    window._i18n.set_language("es")
    assert window.start_page.drop_zone.button.text() == "Seleccionar archivo"
    window._i18n.set_language("en")
    assert window.start_page.drop_zone.button.text() == "Select file"
    assert "never leaves" in window.start_page.callout_title.text()


def test_language_is_remembered(window):
    from PySide6.QtCore import QSettings

    from datacleanr.ui.i18n import I18n

    window._i18n.set_language("es")
    assert I18n(QSettings()).language == "es"
