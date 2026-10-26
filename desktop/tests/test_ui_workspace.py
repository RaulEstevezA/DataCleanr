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
