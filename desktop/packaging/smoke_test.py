"""Checks that the packaged app works: run by the release workflow as `DataCleanr --smoke-test`.

PyInstaller only bundles what it sees imported, so a library loaded in an unusual way can be
missing from the executable even though every test passes. This opens the window and goes
through each library once (Excel, XML, phones, fuzzy matching), then exits with 0.
"""

import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QTimer


def check() -> None:
    from datacleanr.core.dataset import Dataset
    from datacleanr.core.duplicates import SimilarRowsOptions, find_similar_rows
    from datacleanr.core.phone import PhoneOptions, normalize_phone, phone_countries
    from datacleanr.core.similar import SimilarOptions, group_similar_values
    from datacleanr.io.loader import load_file
    from datacleanr.io.xlsx_file import write_workbook

    rows = [["Raúl Estévez", "600 123 456"], ["RAUL ESTEVEZ", "600123456"]]
    with tempfile.TemporaryDirectory() as folder:
        xlsx = Path(folder) / "smoke.xlsx"
        dataset = Dataset("smoke.xlsx", "xlsx", ["Nombre", "Teléfono"], rows, [0, 1])
        write_workbook([("Data", dataset)], ["text", "text"], xlsx)
        assert load_file(xlsx).dataset.rows == rows
        xml = Path(folder) / "smoke.xml"
        xml.write_text("<clientes><cliente><nombre>Ana</nombre></cliente></clientes>", encoding="utf-8")
        assert load_file(xml).dataset.rows == [["Ana"]]

    assert normalize_phone("600 123 456", PhoneOptions("ES", "E164")).value == "+34600123456"
    assert "ES" in phone_countries()
    assert group_similar_values([row[0] for row in rows], SimilarOptions(80, False))
    assert find_similar_rows(rows, SimilarRowsOptions([0, 1], 80, False))


def main() -> None:
    from datacleanr.ui.app import create_app

    app, window = create_app([])
    window.show()

    def run() -> None:
        try:
            check()
        except Exception as error:
            print(f"Smoke test failed: {error!r}", file=sys.stderr)
            app.exit(1)
        else:
            print("Smoke test passed")
            app.exit(0)

    QTimer.singleShot(0, run)
    sys.exit(app.exec())
