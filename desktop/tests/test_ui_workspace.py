from PySide6.QtCore import QCoreApplication, Qt, QThreadPool

from datacleanr.core.history import redo, undo


def wait_for_background():
    QThreadPool.globalInstance().waitForDone()
    QCoreApplication.processEvents()


def test_loading_a_file_shows_the_table(window, tmp_path):
    path = tmp_path / "clientes.csv"
    path.write_text("Empresa;Ciudad\n  TRANSGRAU ;Valencia\nTrans Grau SL;\n", encoding="utf-8")
    window._i18n.set_language("es")
    window.open_file(path)
    wait_for_background()

    assert window.pages.currentWidget() is window.workspace
    model = window.workspace.model
    assert (model.rowCount(), model.columnCount()) == (2, 2)
    assert model.index(0, 0).data() == "  TRANSGRAU "
    assert model.index(1, 1).data() == "vacío"
    assert window.workspace.summary.stats.text() == "2 filas · 2 columnas · UTF-8"


def test_selecting_a_column_highlights_it(window, tmp_path):
    path = tmp_path / "a.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    window.open_file(path)
    wait_for_background()
    window.workspace.select_column(1)
    assert window.workspace.selected_column == 1
    assert window.workspace.summary._buttons[1].isChecked()


def test_unsupported_file_shows_an_error(window, tmp_path):
    path = tmp_path / "old.xls"
    path.write_text("x")
    window._i18n.set_language("en")
    window.open_file(path)
    wait_for_background()
    assert window.pages.currentWidget() is window.start_page
    assert ".xls" in window.start_page.drop_zone.error.text()


def test_excel_sheets_can_be_switched(window, shared_file):
    window.open_file(shared_file("sample.xlsx"))
    wait_for_background()
    assert window.dataset.sheet == "Clientes"
    window.select_sheet("Proveedores")
    assert window.dataset.sheet == "Proveedores"
    window.select_sheet("Vacía")
    assert window.dataset.sheet == "Proveedores"


def load(window, tmp_path, text):
    path = tmp_path / "clientes.csv"
    path.write_text(text, encoding="utf-8")
    window.open_file(path)
    wait_for_background()


def test_preview_apply_undo_and_redo(window, tmp_path):
    window._i18n.set_language("es")
    load(window, tmp_path, "Contacto;Ciudad\n  ana ruiz ;Bilbao\nJuan;Valencia\n laura;Madrid\n")
    workspace = window.workspace
    workspace.select_column(0)
    panel = workspace.panel
    panel.select_action("trim")
    assert [(c.original, c.proposed) for c in panel.model.changes] == [("  ana ruiz ", "ana ruiz"), (" laura", "laura")]

    # Reject the second change, apply only the first
    panel.model.setData(panel.model.index(1, 0), Qt.CheckState.Unchecked.value, Qt.ItemDataRole.CheckStateRole)
    assert panel.apply_button.text() == "Aplicar 1 cambio"
    panel.apply()
    assert window.dataset.rows[0][0] == "ana ruiz"
    assert window.dataset.rows[2][0] == " laura"
    assert "1 cambio aplicado" in workspace.notice.text()
    assert "1 celda modificada" in workspace.summary.stats.text()

    window.move_in_history(undo)
    assert window.dataset.rows[0][0] == "  ana ruiz "
    assert not workspace.summary.undo_button.isEnabled()
    window.move_in_history(redo)
    assert window.dataset.rows[0][0] == "ana ruiz"


def test_no_changes_message(window, tmp_path):
    window._i18n.set_language("en")
    load(window, tmp_path, "a,b\nx,y\n")
    window.workspace.select_column(0)
    window.workspace.panel.select_action("trim")
    assert "already clean" in window.workspace.panel.info.text()


def test_normalizers_show_issues_and_preview(window, tmp_path):
    from PySide6.QtCore import QSettings

    QSettings().setValue("phoneOptions", '{"defaultCountry": "ES", "format": "E164"}')
    window._i18n.set_language("es")
    load(window, tmp_path, "Teléfono;Fecha;Importe\n600 123 456;13/07/2024;€12,50\nno tiene;31/04/2024;$3.99\n")
    panel = window.workspace.panel

    window.workspace.select_column(0)
    panel.select_action("phone")
    assert [c.proposed for c in panel.model.changes] == ["+34600123456"]
    assert panel.issues.isVisible() and "1 valor no se puede normalizar" in panel.issues.message.text()

    window.workspace.select_column(2)
    panel.select_action("amount")
    assert panel.currency_warning.isVisible() and "EUR, USD" in panel.currency_warning.text()


def test_custom_replace_and_profile_step(window, tmp_path):
    load(window, tmp_path, "Empresa\nTransgrau s.l\nOtra\n")
    window.workspace.select_column(0)
    panel = window.workspace.panel
    panel.select_action("custom")
    assert not panel.preview.isVisible()
    form = panel.forms["custom"]
    form.find.setText("TRANSGRAU S.L")
    form.replacement.setText("TransGrau SL")
    assert [c.proposed for c in panel.model.changes] == ["TransGrau SL"]
    assert panel.profile_step("custom") == {
        "type": "replace",
        "column": "Empresa",
        "find": "TRANSGRAU S.L",
        "replacement": "TransGrau SL",
        "wholeCell": True,
        "ignoreCase": True,
    }


def test_spanish_country_names():
    from datacleanr.ui.option_forms import country_name

    assert country_name("ES", "es") == "España (ES)"
    assert country_name("PT", "es") == "Portugal (PT)"
    assert country_name("DE", "en") == "Germany (DE)"
    assert country_name("XK", "es") == "Kosovo (XK)"


def test_unify_similar_values(window, tmp_path):
    window._i18n.set_language("es")
    load(window, tmp_path, "Nombre\nRaúl Estévez\nRaúl Estévez\nRAUL ESTEVEZ\nraul estévez\nAna Ruiz\n")
    window.workspace.select_column(0)
    panel = window.workspace.panel
    panel.select_action("similar")
    wait_for_background()

    form = panel.forms["similar"]
    assert len(form._card_widgets) == 1
    assert sorted(c.proposed for c in panel.model.changes) == ["Raúl Estévez", "Raúl Estévez"]

    card = form._card_widgets[0]
    card.custom.setText("Raúl Estévez Á.")
    card._custom_edited()
    assert {c.proposed for c in panel.model.changes} == {"Raúl Estévez Á."}
    assert panel.profile_step("similar")["mapping"] == [
        {"from": "Raúl Estévez", "to": "Raúl Estévez Á."},
        {"from": "RAUL ESTEVEZ", "to": "Raúl Estévez Á."},
        {"from": "raul estévez", "to": "Raúl Estévez Á."},
    ]

    card.included.setChecked(False)
    assert not panel.model.changes
