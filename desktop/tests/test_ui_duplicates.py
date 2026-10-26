from datacleanr.core.dataset import Dataset
from datacleanr.ui.duplicates_dialog import DuplicatesDialog

from .test_ui_workspace import wait_for_background

ROWS = [
    ["1", "Juan Pérez", "juan@transgrau.com", ""],
    ["2", "Ana Ruiz", "ana@lnorte.es", ""],
    ["3", "juan perez", "", "600 123 456"],
    ["4", "Ana Ruíz", "", "944 555 666"],
    ["5", "Juan Pérez", "juan@transgrau.com", "611 222 333"],
]
DATASET = Dataset("p.csv", "csv", ["ID", "Nombre", "Email", "Teléfono"], ROWS, list(range(5)))


def dialog(window) -> DuplicatesDialog:
    window._i18n.set_language("es")
    result = DuplicatesDialog(window._i18n, DATASET, window)
    wait_for_background()
    return result


def test_exact_duplicates_with_merge(window):
    d = dialog(window)
    # Compare by name and email only
    for column in (0, 3):
        d.column_buttons[column].setChecked(False)
    d._recompute()
    wait_for_background()
    assert [group.rows for group in d._groups] == [[0, 4]]
    assert d.remove_button.text() == "Eliminar 1 fila"
    assert "se rellenará 1 celda vacía" in d.summary.text()
    d._remove()
    assert d.result.removed == 1 and d.result.filled == 1
    assert d.result.dataset.rows[0] == ["1", "Juan Pérez", "juan@transgrau.com", "611 222 333"]
    assert d.result.profile_step == {
        "type": "removeDuplicates",
        "columns": ["Nombre", "Email"],
        "ignoreCaseAndSpaces": False,
        "merge": True,
    }


def test_possible_duplicates_need_confirmation(window):
    d = dialog(window)
    d.similar_button.setChecked(True)
    for column in (0, 2, 3):
        d.column_buttons[column].setChecked(False)
    d._recompute()
    wait_for_background()
    assert [group.rows for group in d._groups] == [[0, 2, 4], [1, 3]]
    assert not d.remove_button.isEnabled()
    d._views[1].included.setChecked(True)
    assert d.remove_button.text() == "Eliminar 1 fila"
    d._remove()
    assert d.result.mode == "similar" and d.result.profile_step is None
    assert d.result.dataset.row_ids == [0, 1, 2, 4]


def test_window_records_the_removal_in_history(window, tmp_path):
    from .test_ui_workspace import load

    load(window, tmp_path, "Nombre;Email\nAna;a@x.com\nAna;a@x.com\nJuan;j@x.com\n")
    d = DuplicatesDialog(window._i18n, window.dataset, window)
    wait_for_background()
    d._remove()
    window.apply_removal(d.result)
    assert len(window.dataset.rows) == 2
    assert (
        "1 fila eliminada" in window.workspace.summary.stats.text()
        or "1 row removed" in window.workspace.summary.stats.text()
    )
    assert window.history.current.operation.kind == "removeRows"
