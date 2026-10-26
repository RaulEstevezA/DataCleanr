# PyInstaller build of the desktop app. From desktop/:
#
#     pyinstaller packaging/datacleanr.spec
#
# Result in dist/: DataCleanr.app on macOS, a DataCleanr folder with DataCleanr.exe on Windows
# and with the DataCleanr binary on Linux.

import sys
from pathlib import Path

HERE = Path(SPECPATH)
ROOT = HERE.parent

# Qt modules the app doesn't use. PyInstaller follows imports, but the PySide6 hooks pull in
# some of these through plugins; leaving them out keeps the download much smaller.
EXCLUDED = [
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtWebChannel",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickWidgets",
    "PySide6.QtMultimedia",
    "PySide6.QtPdf",
    "PySide6.Qt3DCore",
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtNetwork",
    "PySide6.QtOpenGL",
    "PySide6.QtSql",
    "PySide6.QtTest",
    "tkinter",
    "pandas",
    # openpyxl imports it only to embed images in sheets
    "PIL",
]

# Qt libraries and plugins that come in through other plugins (the virtual keyboard brings
# QML and Qt Quick, the PDF image plugin brings QtPdf). Matched against the bundled paths.
UNUSED_QT = ["QtQml", "QtQuick", "QtVirtualKeyboard", "QtPdf", "QtNetwork", "QtOpenGL", "virtualkeyboard", "qpdf"]

analysis = Analysis(
    [str(HERE / "launcher.py")],
    pathex=[str(ROOT)],
    datas=[(str(ROOT / "datacleanr" / "assets"), "datacleanr/assets")],
    # The window icon is an SVG: Qt loads it through the QtSvg image plugin
    hiddenimports=["PySide6.QtSvg"],
    excludes=EXCLUDED,
)
analysis.binaries = [b for b in analysis.binaries if not any(name in b[0] for name in UNUSED_QT)]
analysis.datas = [d for d in analysis.datas if not any(name in d[0] for name in UNUSED_QT)]
pyz = PYZ(analysis.pure)

icon = str(HERE / ("icon.ico" if sys.platform == "win32" else "icon.icns"))
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="DataCleanr",
    console=False,
    icon=icon,
)
collected = COLLECT(exe, analysis.binaries, analysis.datas, name="DataCleanr")

if sys.platform == "darwin":
    app = BUNDLE(
        collected,
        name="DataCleanr.app",
        icon=icon,
        bundle_identifier="io.github.raulesteveza.datacleanr",
        info_plist={
            "CFBundleShortVersionString": "0.1.0",
            "NSHighResolutionCapable": True,
            # Light and dark appearance follow the system
            "NSRequiresAquaSystemAppearance": False,
        },
    )
