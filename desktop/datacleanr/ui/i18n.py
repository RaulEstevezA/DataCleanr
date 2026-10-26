"""English and Spanish texts. Mirrors web/src/i18n/messages.ts for the texts both versions share.

Texts with numbers are functions so they can pick singular or plural and format the number
with the language's separators.
"""

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QLocale, QObject, QSettings, Signal


def _format(language: str) -> Callable[[int], str]:
    locale = QLocale(QLocale.Language.English if language == "en" else QLocale.Language.Spanish)
    return lambda n: locale.toString(n)


@dataclass(frozen=True)
class Messages:
    tagline: str
    intro_description: str
    privacy_title: str
    privacy_points: tuple[str, ...]
    import_title: str
    import_description: str
    import_button: str
    import_hint: str
    import_loading: str
    language_label: str


EN = Messages(
    tagline="Clean, normalize and unify tabular data",
    intro_description=(
        "Load a messy file, review every change as original → proposed and export clean data: trims, case, "
        "phone numbers, dates, amounts, different spellings of the same value "
        "(Raúl Estévez / RAUL ESTEVEZ / raul estévez) and duplicate rows."
    ),
    privacy_title="Your data never leaves this computer",
    privacy_points=(
        "Files are read and processed on your device. Nothing is uploaded anywhere.",
        "Nothing changes without your confirmation, and every step can be undone.",
        "The original file is never modified: you save a cleaned copy.",
    ),
    import_title="Import a file to get started",
    import_description="Load a CSV, Excel (.xlsx), JSON or XML file to preview its data, pick a column and clean it.",
    import_button="Select file",
    import_hint="or drag and drop it here",
    import_loading="Reading file...",
    language_label="Language",
)

ES = Messages(
    tagline="Limpia, normaliza y unifica datos tabulares",
    intro_description=(
        "Carga un archivo sucio, revisa cada cambio como original → propuesto y exporta los datos limpios: "
        "espacios, mayúsculas, teléfonos, fechas, importes, distintas formas de escribir lo mismo "
        "(Raúl Estévez / RAUL ESTEVEZ / raul estévez) y filas duplicadas."
    ),
    privacy_title="Tus datos no salen de este ordenador",
    privacy_points=(
        "Los archivos se leen y se procesan en tu equipo. No se sube nada a ningún sitio.",
        "Nada cambia sin tu confirmación, y cualquier paso se puede deshacer.",
        "El archivo original nunca se modifica: guardas una copia limpia.",
    ),
    import_title="Importa un archivo para empezar",
    import_description=(
        "Carga un archivo CSV, Excel (.xlsx), JSON o XML para ver sus datos, elegir una columna y limpiarla."
    ),
    import_button="Seleccionar archivo",
    import_hint="o arrástralo aquí",
    import_loading="Leyendo archivo...",
    language_label="Idioma",
)

MESSAGES = {"en": EN, "es": ES}


class I18n(QObject):
    """Current language, remembered between sessions. Widgets connect to `changed` to retranslate."""

    changed = Signal()

    def __init__(self, settings: QSettings):
        super().__init__()
        self._settings = settings
        stored = settings.value("language")
        system = QLocale.system().name()[:2]
        self.language = stored if stored in MESSAGES else system if system in MESSAGES else "en"

    @property
    def t(self) -> Messages:
        return MESSAGES[self.language]

    @property
    def format_number(self) -> Callable[[int], str]:
        return _format(self.language)

    def set_language(self, language: str) -> None:
        if language == self.language:
            return
        self.language = language
        self._settings.setValue("language", language)
        self.changed.emit()
