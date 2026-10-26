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


_en = _format("en")
_es = _format("es")


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
    privacy_short: str
    import_another: str
    sheet: str
    detected_columns: str
    empty_cell: str
    row_count: Callable[[int], str]
    column_count: Callable[[int], str]
    error_unsupported: str
    error_old_excel: str
    error_parse_csv: str
    error_parse_excel: str
    error_parse_json: dict[str, str]
    error_parse_xml: dict[str, str]
    error_read: str
    empty_sheet: Callable[[str], str]


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
    privacy_short="Processed locally",
    import_another="Import another file",
    sheet="Sheet",
    detected_columns="Detected columns",
    empty_cell="empty",
    row_count=lambda n: "1 row" if n == 1 else f"{_en(n)} rows",
    column_count=lambda n: "1 column" if n == 1 else f"{_en(n)} columns",
    error_unsupported="Only CSV, Excel (.xlsx), JSON and XML files are supported.",
    error_old_excel="The old Excel format (.xls) is not supported. Open it in Excel and save it as .xlsx.",
    error_parse_csv="The file could not be read. Check that it is a valid, non-empty CSV.",
    error_parse_excel="The Excel file could not be read, or all its sheets are empty.",
    error_parse_json={
        "invalid": "The file is not valid JSON.",
        "unsupported": "This JSON does not look like a table. Supported: a list of objects, a list of lists, "
        "or an object holding one of those lists.",
        "empty": "The JSON list is empty.",
    },
    error_parse_xml={
        "invalid": "The file is not well-formed XML.",
        "unsupported": "No repeated elements were found to use as rows in this XML.",
    },
    error_read="The file could not be opened.",
    empty_sheet=lambda sheet: f"The sheet “{sheet}” is empty.",
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
    privacy_short="Procesado en local",
    import_another="Importar otro archivo",
    sheet="Hoja",
    detected_columns="Columnas detectadas",
    empty_cell="vacío",
    row_count=lambda n: "1 fila" if n == 1 else f"{_es(n)} filas",
    column_count=lambda n: "1 columna" if n == 1 else f"{_es(n)} columnas",
    error_unsupported="Solo se admiten archivos CSV, Excel (.xlsx), JSON y XML.",
    error_old_excel="El formato antiguo de Excel (.xls) no está soportado. Ábrelo en Excel y guárdalo como .xlsx.",
    error_parse_csv="No se ha podido leer el archivo. Comprueba que sea un CSV válido y no esté vacío.",
    error_parse_excel="No se ha podido leer el archivo Excel, o todas sus hojas están vacías.",
    error_parse_json={
        "invalid": "El archivo no es un JSON válido.",
        "unsupported": "Este JSON no parece una tabla. Se admite una lista de objetos, una lista de listas "
        "o un objeto que contenga una de esas listas.",
        "empty": "La lista del JSON está vacía.",
    },
    error_parse_xml={
        "invalid": "El archivo no es un XML bien formado.",
        "unsupported": "No se han encontrado elementos repetidos que usar como filas en este XML.",
    },
    error_read="No se ha podido abrir el archivo.",
    empty_sheet=lambda sheet: f"La hoja «{sheet}» está vacía.",
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
