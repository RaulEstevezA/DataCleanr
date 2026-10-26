import json

from PySide6.QtWidgets import QMessageBox

from datacleanr.core.profile import parse_profile, serialize_profile
from datacleanr.ui.history_dialog import HistoryDialog, profile_file_name

from .conftest import load_cases
from .test_ui_workspace import load, wait_for_background


def clean_contacts(window, tmp_path):
    window._i18n.set_language("es")
    load(window, tmp_path, "Contacto;Ciudad\n  ana   ruiz ;Bilbao\nJUAN pérez;Valencia\n")
    panel = window.workspace.panel
    window.workspace.select_column(0)
    for action in ("trim", "collapseSpaces", "titleCase"):
        panel.select_action(action)
        panel.apply()


def test_history_lists_steps_and_goes_back(window, tmp_path):
    clean_contacts(window, tmp_path)
    dialog = HistoryDialog(window._i18n, window.history, window)
    assert dialog.steps.count() == 4
    assert dialog.steps.item(3).text().endswith("Primera En Mayúscula en «Contacto» (2 celdas)")
    dialog.steps.setCurrentRow(1)
    dialog._go_to()
    assert dialog.go_to_index == 1


def test_saved_profile_matches_the_web_format(window, tmp_path):
    clean_contacts(window, tmp_path)
    dialog = HistoryDialog(window._i18n, window.history, window)
    dialog.name.setText("Contactos")
    profile = dialog.profile()
    data = json.loads(serialize_profile(profile))
    assert data["format"] == "datacleanr-profile" and data["version"] == 1
    assert [step["transform"] for step in data["steps"]] == ["trim", "collapseSpaces", "titleCase"]
    assert profile_file_name("Facturación 2024 / España") == "facturacion-2024-espana.datacleanr.json"


def test_apply_profile_adds_one_history_step_per_change(window, tmp_path):
    window._i18n.set_language("es")
    case = load_cases("profile.json")["run"][0]
    header = ";".join(case["columns"])
    body = "\n".join(";".join(row) for row in case["rows"])
    load(window, tmp_path, f"{header}\n{body}\n")
    profile = parse_profile(json.dumps(case["profile"]))
    from datacleanr.core.profile import run_profile

    window.apply_profile_results(profile, run_profile(window.dataset, profile))
    assert window.dataset.rows == case["expected"]["rows"]
    # 11 steps, one skipped (missing column): 10 history steps plus the import
    assert len(window.history.entries) == 11
    assert "aplicado (10 pasos)" in window.workspace.notice.text()


def test_import_another_asks_before_discarding(window, tmp_path, monkeypatch):
    clean_contacts(window, tmp_path)
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.No)
    window.show_start()
    assert window.pages.currentWidget() is window.workspace
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.show_start()
    assert window.pages.currentWidget() is window.start_page


def test_invalid_profile_shows_a_warning(window, tmp_path):
    clean_contacts(window, tmp_path)
    bad = tmp_path / "bad.json"
    bad.write_text('{"a": 1}', encoding="utf-8")
    window.load_profile(bad)
    wait_for_background()
    assert window.workspace.notice.text() == "Este archivo no es un perfil de DataCleanr."
