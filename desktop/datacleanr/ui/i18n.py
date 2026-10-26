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
    clean_column: Callable[[str], str]
    transformation: str
    choose_transformation: str
    transform_names: dict[str, str]
    no_changes: str
    original: str
    proposed: str
    accept_all: str
    changes_selected: Callable[[int, int], str]
    cancel: str
    apply_changes: Callable[[int], str]
    changes_applied: Callable[[int, str], str]
    modified_cells: Callable[[int], str]
    undo: str
    redo: str
    find_label: str
    replace_label: str
    find_placeholder: str
    replace_placeholder: str
    whole_cell: str
    ignore_case: str
    no_matches: str
    normalize_issues: Callable[[int], str]
    show_values: str
    hide_values: str
    phone_country: str
    phone_format: str
    phone_format_names: dict[str, str]
    phone_hint: str
    date_input_order: str
    date_order_names: dict[str, str]
    date_format: str
    date_format_names: dict[str, str]
    date_two_digit_limit: str
    date_hint: str
    amount_ambiguous: str
    amount_separator_names: dict[str, str]
    amount_format: str
    amount_format_names: dict[str, str]
    amount_two_decimals: str
    amount_hint: str
    amount_mixed_currencies: Callable[[str], str]
    similar_threshold: Callable[[int], str]
    similar_threshold_hint: str
    similar_ignore_legal_forms: str
    similar_searching: str
    similar_none: str
    similar_truncated: Callable[[int, int], str]
    similar_group_summary: Callable[[int, int], str]
    similar_choose_value: str
    similar_other: str
    find_duplicates: str
    duplicates_title: str
    duplicates_exact: str
    duplicates_similar: str
    duplicates_compare: str
    duplicates_compare_similar: str
    duplicates_ignore_case: str
    duplicates_hint: str
    duplicates_similar_hint: str
    duplicates_merge: str
    duplicates_searching: str
    duplicates_no_columns: str
    duplicates_none: str
    duplicates_group: Callable[[int], str]
    duplicates_similar_group: Callable[[int], str]
    duplicates_keep: str
    duplicates_score: str
    duplicates_result: str
    duplicates_conflict: str
    duplicates_truncated: Callable[[int, int], str]
    duplicates_summary: Callable[[int, int], str]
    duplicates_filled: Callable[[int], str]
    duplicates_remove: Callable[[int], str]
    rows_removed: Callable[[int, int], str]
    removed_rows: Callable[[int], str]
    export: str
    export_title: str
    export_delimiter: str
    delimiter_names: dict[str, str]
    export_csv_hint: str
    export_types_hint: str
    export_column: str
    export_type: str
    export_example: str
    export_suggested: str
    column_type_names: dict[str, str]
    export_fallbacks: Callable[[int], str]
    export_error: str
    exporting: str
    save_as: str
    saved: Callable[[str], str]
    export_split: str
    export_required: str
    split_counts: Callable[[int, int], str]
    split_single_part: str
    export_split_csv_hint: str
    export_split_xlsx_hint: str
    sheet_complete: str
    sheet_incomplete: str
    history: str
    history_title: Callable[[int], str]
    history_import: Callable[[str], str]
    history_cells: Callable[[str, str, int], str]
    history_remove_exact: Callable[[int, int], str]
    history_remove_similar: Callable[[int, int], str]
    history_hint: str
    history_go_to: str
    profile_save_label: str
    profile_default_name: str
    profile_save: Callable[[int], str]
    profile_not_replayable: Callable[[int], str]
    profile_save_hint: str
    profile_saved: Callable[[str], str]
    load_profile: str
    profile_title: Callable[[str], str]
    profile_apply_hint: str
    profile_skipped: str
    profile_summary: Callable[[int, int], str]
    profile_apply: Callable[[int], str]
    profile_applied: Callable[[str, int], str]
    profile_error: dict[str, str]
    profile_step_cells: Callable[[str, str], str]
    profile_step_map: Callable[[str, int], str]
    profile_step_duplicates: Callable[[str], str]
    confirm_discard_title: str
    confirm_discard: str


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
    clean_column=lambda column: f"Clean column “{column}”",
    transformation="Transformation",
    choose_transformation="Choose a transformation...",
    transform_names={
        "trim": "Trim spaces",
        "collapseSpaces": "Collapse repeated spaces",
        "lowercase": "lowercase",
        "uppercase": "UPPERCASE",
        "titleCase": "Title Case",
        "custom": "Custom replace",
        "phone": "Normalize phone numbers",
        "date": "Normalize dates",
        "amount": "Normalize amounts",
        "similar": "Unify similar values",
    },
    no_changes="Nothing to change: this column is already clean for this transformation.",
    original="Original",
    proposed="Proposed",
    accept_all="Accept all",
    changes_selected=lambda accepted, total: (
        f"{_en(accepted)} of {_en(total)} {'change' if total == 1 else 'changes'} selected"
    ),
    cancel="Cancel",
    apply_changes=lambda n: "Apply 1 change" if n == 1 else f"Apply {_en(n)} changes",
    changes_applied=lambda n, column: (
        f"1 change applied to “{column}”." if n == 1 else f"{_en(n)} changes applied to “{column}”."
    ),
    modified_cells=lambda n: "1 cell modified" if n == 1 else f"{_en(n)} cells modified",
    undo="Undo",
    redo="Redo",
    find_label="Find",
    replace_label="Replace with",
    find_placeholder="Text to find",
    replace_placeholder="New value",
    whole_cell="Match whole cell",
    ignore_case="Ignore upper/lower case",
    no_matches="No cell matches the text you are looking for.",
    normalize_issues=lambda n: (
        "1 value could not be normalized and will be left unchanged. Review it by hand."
        if n == 1
        else f"{_en(n)} values could not be normalized and will be left unchanged. Review them by hand."
    ),
    show_values="Show values",
    hide_values="Hide values",
    phone_country="Default country (numbers without prefix)",
    phone_format="Output format",
    phone_format_names={"E164": "E.164 (databases)", "INTERNATIONAL": "International", "NATIONAL": "National"},
    phone_hint=(
        "Numbers that already have a prefix (+33, +44...) keep their country. In national format, "
        "foreign numbers stay international so their country is not lost."
    ),
    date_input_order="How are dates written in this column?",
    date_order_names={"DMY": "Day / month / year", "MDY": "Month / day / year"},
    date_format="Output format",
    date_format_names={"ISO": "ISO 8601 (databases)", "DMY": "DD/MM/YYYY", "MDY": "MM/DD/YYYY"},
    date_two_digit_limit="Two-digit years: up to which year are they 2000s? (Excel uses 29)",
    date_hint="Dates starting with the year (2024-07-13) are always read as year-month-day.",
    amount_ambiguous="Decimal separator when in doubt (e.g. 1.234)",
    amount_separator_names={",": "Comma", ".": "Dot"},
    amount_format="Output format",
    amount_format_names={
        "DOT": "Dot decimal (databases)",
        "COMMA": "Comma decimal",
        "COMMA_GROUPED": "Spanish style",
        "DOT_GROUPED": "English style",
    },
    amount_two_decimals="Always two decimals (never rounded: extra decimals go to review)",
    amount_hint=(
        "Unambiguous values are detected automatically: 12063.99 and 5837,32 are decimals, 1.234.567 is "
        "thousands. Currency symbols (€, $, £, EUR...) are removed."
    ),
    amount_mixed_currencies=lambda currencies: (
        f"This column mixes currencies ({currencies}). Removing the symbols loses that information: "
        "review before applying."
    ),
    similar_threshold=lambda n: f"Similarity: {n}%",
    similar_threshold_hint="Lower groups more values (and more false matches); higher is stricter.",
    similar_ignore_legal_forms="Ignore legal forms when comparing (S.L., S.A., Inc...)",
    similar_searching="Looking for similar values...",
    similar_none="No similar values found in this column with this similarity.",
    similar_truncated=lambda shown, total: (
        f"Showing the first {_en(shown)} of {_en(total)} groups. Hidden groups use the suggested value."
    ),
    similar_group_summary=lambda variants, cells: (
        f"{variants} variants · {'1 cell' if cells == 1 else f'{_en(cells)} cells'}"
    ),
    similar_choose_value="Unify as:",
    similar_other="Other:",
    find_duplicates="Find duplicate rows",
    duplicates_title="Duplicate rows",
    duplicates_exact="Exact",
    duplicates_similar="Possible (similar)",
    duplicates_compare="Columns to compare (two rows are duplicates if they match in all of them):",
    duplicates_compare_similar=(
        "Columns to compare (rows are scored by their average similarity; leave out columns that are "
        "always different, like IDs):"
    ),
    duplicates_ignore_case="Ignore upper/lower case and extra spaces",
    duplicates_hint="Rows with all compared columns empty are never treated as duplicates.",
    duplicates_similar_hint=(
        "Columns where one of the two rows is empty are skipped, and at least half of the compared columns "
        "must have data. Groups are not selected by default: confirm the ones that are real duplicates."
    ),
    duplicates_merge="Combine rows: fill empty cells of the kept row with data from the removed ones",
    duplicates_searching="Looking for duplicates...",
    duplicates_no_columns="Select at least one column to compare.",
    duplicates_none="No duplicate rows found.",
    duplicates_group=lambda n: f"{_en(n)} identical rows",
    duplicates_similar_group=lambda n: f"{_en(n)} similar rows",
    duplicates_keep="Keep",
    duplicates_score="Similarity",
    duplicates_result="Result",
    duplicates_conflict="The removed rows have different values here; the first one is used. Check it.",
    duplicates_truncated=lambda shown, total: (
        f"Showing the first {_en(shown)} of {_en(total)} groups. Hidden exact groups keep their first row; "
        "hidden possible groups are not modified."
    ),
    duplicates_summary=lambda groups, rows: (
        f"{'1 group' if groups == 1 else f'{_en(groups)} groups'} · "
        f"{'1 row' if rows == 1 else f'{_en(rows)} rows'} will be removed"
    ),
    duplicates_filled=lambda n: "1 empty cell will be filled" if n == 1 else f"{_en(n)} empty cells will be filled",
    duplicates_remove=lambda n: "Remove 1 row" if n == 1 else f"Remove {_en(n)} rows",
    rows_removed=lambda n, filled: (
        f"{'1 duplicate row removed' if n == 1 else f'{_en(n)} duplicate rows removed'}"
        + (f" and {'1 empty cell' if filled == 1 else f'{_en(filled)} empty cells'} filled" if filled else "")
        + "."
    ),
    removed_rows=lambda n: "1 row removed" if n == 1 else f"{_en(n)} rows removed",
    export="Export",
    export_title="Export",
    export_delimiter="Column separator",
    delimiter_names={";": "Semicolon ( ; ), Excel in Spanish", ",": "Comma ( , ), international", "\t": "Tab"},
    export_csv_hint="Saved as UTF-8 so accents display correctly in Excel and databases.",
    export_types_hint=(
        "Choose how each column is saved. The suggestion fits every value of the column; values that cannot be "
        "converted without losing information (007, 1234,56, 13/07/2024...) are saved as text."
    ),
    export_column="Column",
    export_type="Save as",
    export_example="Example",
    export_suggested="suggested",
    column_type_names={"text": "Text", "number": "Number", "date": "Date", "boolean": "True/False"},
    export_fallbacks=lambda n: "1 value will stay as text" if n == 1 else f"{_en(n)} values will stay as text",
    export_error="The file could not be saved. Check that it is not open in another program and try again.",
    exporting="Saving...",
    save_as="Save as...",
    saved=lambda path: f"Saved to {path}",
    export_split="Separate complete and incomplete rows",
    export_required="Required columns (a row is complete when all of them have a value):",
    split_counts=lambda complete, incomplete: (
        f"{'1 complete row' if complete == 1 else f'{_en(complete)} complete rows'} · "
        f"{'1 incomplete row' if incomplete == 1 else f'{_en(incomplete)} incomplete rows'}"
    ),
    split_single_part="One of the parts is empty, so only the other one will be exported.",
    export_split_csv_hint="Two files are saved next to the name you choose, ending in _complete and _incomplete.",
    export_split_xlsx_hint="One Excel file with two sheets: “Complete” and “Incomplete”.",
    sheet_complete="Complete",
    sheet_incomplete="Incomplete",
    history="History",
    history_title=lambda steps: f"History ({'1 step' if steps == 1 else f'{_en(steps)} steps'})",
    history_import=lambda file: f"Import “{file}”",
    history_cells=lambda action, column, count: (
        f"{action} in “{column}” ({'1 cell' if count == 1 else f'{_en(count)} cells'})"
    ),
    history_remove_exact=lambda n, filled: (
        f"Remove exact duplicates ({'1 row' if n == 1 else f'{_en(n)} rows'}"
        + (f", {_en(filled)} filled" if filled else "")
        + ")"
    ),
    history_remove_similar=lambda n, filled: (
        f"Remove possible duplicates ({'1 row' if n == 1 else f'{_en(n)} rows'}"
        + (f", {_en(filled)} filled" if filled else "")
        + ")"
    ),
    history_hint="Double-click a step, or select it and press the button, to go back to it.",
    history_go_to="Go to this step",
    profile_save_label="Save the steps as a cleaning profile",
    profile_default_name="My cleaning profile",
    profile_save=lambda n: "Save profile (1 step)" if n == 1 else f"Save profile ({_en(n)} steps)",
    profile_not_replayable=lambda n: (
        f"{'1 step' if n == 1 else f'{_en(n)} steps'} cannot be saved in a profile "
        "(possible duplicates need a person to confirm them)."
    ),
    profile_save_hint=(
        "A profile repeats each step on a whole column; changes rejected row by row are not remembered. "
        "Duplicates keep the first row. Profiles also work in the web version."
    ),
    profile_saved=lambda path: f"Profile saved to {path}",
    load_profile="Apply profile",
    profile_title=lambda name: f"Profile “{name}”",
    profile_apply_hint=(
        "Each step is checked against the current data before applying anything. Every applied step is added to "
        "the history, so it can be undone."
    ),
    profile_skipped="Skipped: column not found",
    profile_summary=lambda effective, total: f"{_en(effective)} of {_en(total)} steps will change data",
    profile_apply=lambda n: "Apply 1 step" if n == 1 else f"Apply {_en(n)} steps",
    profile_applied=lambda name, n: f"Profile “{name}” applied ({'1 step' if n == 1 else f'{_en(n)} steps'}).",
    profile_error={
        "invalid": "This file is not a DataCleanr profile.",
        "version": "This profile was created with a newer version of DataCleanr.",
        "step": "The profile has an invalid step.",
    },
    profile_step_cells=lambda action, column: f"{action} in “{column}”",
    profile_step_map=lambda column, n: f"Replace values in “{column}” ({'1 rule' if n == 1 else f'{_en(n)} rules'})",
    profile_step_duplicates=lambda columns: f"Remove exact duplicates comparing {columns}",
    confirm_discard_title="Unsaved changes",
    confirm_discard="You have changes that have not been exported. Discard them?",
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
    clean_column=lambda column: f"Limpiar columna «{column}»",
    transformation="Transformación",
    choose_transformation="Elige una transformación...",
    transform_names={
        "trim": "Quitar espacios de los extremos",
        "collapseSpaces": "Quitar espacios repetidos",
        "lowercase": "minúsculas",
        "uppercase": "MAYÚSCULAS",
        "titleCase": "Primera En Mayúscula",
        "custom": "Reemplazo personalizado",
        "phone": "Normalizar teléfonos",
        "date": "Normalizar fechas",
        "amount": "Normalizar importes",
        "similar": "Unificar valores parecidos",
    },
    no_changes="No hay nada que cambiar: esta columna ya está limpia para esta transformación.",
    original="Original",
    proposed="Propuesto",
    accept_all="Aceptar todos",
    changes_selected=lambda accepted, total: (
        f"{_es(accepted)} de {_es(total)} {'cambio seleccionado' if total == 1 else 'cambios seleccionados'}"
    ),
    cancel="Cancelar",
    apply_changes=lambda n: "Aplicar 1 cambio" if n == 1 else f"Aplicar {_es(n)} cambios",
    changes_applied=lambda n, column: (
        f"1 cambio aplicado en «{column}»." if n == 1 else f"{_es(n)} cambios aplicados en «{column}»."
    ),
    modified_cells=lambda n: "1 celda modificada" if n == 1 else f"{_es(n)} celdas modificadas",
    undo="Deshacer",
    redo="Rehacer",
    find_label="Buscar",
    replace_label="Reemplazar por",
    find_placeholder="Texto a buscar",
    replace_placeholder="Nuevo valor",
    whole_cell="Coincidir con la celda completa",
    ignore_case="Ignorar mayúsculas/minúsculas",
    no_matches="Ninguna celda coincide con el texto buscado.",
    normalize_issues=lambda n: (
        "1 valor no se puede normalizar y se dejará sin cambios. Revísalo a mano."
        if n == 1
        else f"{_es(n)} valores no se pueden normalizar y se dejarán sin cambios. Revísalos a mano."
    ),
    show_values="Ver valores",
    hide_values="Ocultar valores",
    phone_country="País por defecto (números sin prefijo)",
    phone_format="Formato de salida",
    phone_format_names={"E164": "E.164 (bases de datos)", "INTERNATIONAL": "Internacional", "NATIONAL": "Nacional"},
    phone_hint=(
        "Los números que ya tienen prefijo (+33, +44...) mantienen su país. En formato nacional, los "
        "extranjeros se dejan en internacional para no perder su país."
    ),
    date_input_order="¿Cómo están escritas las fechas en esta columna?",
    date_order_names={"DMY": "Día / mes / año", "MDY": "Mes / día / año"},
    date_format="Formato de salida",
    date_format_names={"ISO": "ISO 8601 (bases de datos)", "DMY": "DD/MM/AAAA", "MDY": "MM/DD/AAAA"},
    date_two_digit_limit="Años de dos cifras: ¿hasta qué año son del 2000? (Excel usa el 29)",
    date_hint="Las fechas que empiezan por el año (2024-07-13) se leen siempre como año-mes-día.",
    amount_ambiguous="Separador decimal en caso de duda (ej. 1.234)",
    amount_separator_names={",": "Coma", ".": "Punto"},
    amount_format="Formato de salida",
    amount_format_names={
        "DOT": "Punto decimal (bases de datos)",
        "COMMA": "Coma decimal",
        "COMMA_GROUPED": "Formato español",
        "DOT_GROUPED": "Formato inglés",
    },
    amount_two_decimals="Siempre dos decimales (nunca redondea: si hay más, van a revisión)",
    amount_hint=(
        "Los valores sin ambigüedad se detectan solos: 12063.99 y 5837,32 son decimales, 1.234.567 son miles. "
        "Se quitan los símbolos de moneda (€, $, £, EUR...)."
    ),
    amount_mixed_currencies=lambda currencies: (
        f"Esta columna mezcla monedas ({currencies}). Al quitar los símbolos se pierde esa información: "
        "revísala antes de aplicar."
    ),
    similar_threshold=lambda n: f"Parecido: {n}%",
    similar_threshold_hint="Más bajo agrupa más valores (y más falsos parecidos); más alto es más estricto.",
    similar_ignore_legal_forms="Ignorar formas jurídicas al comparar (S.L., S.A., Inc...)",
    similar_searching="Buscando valores parecidos...",
    similar_none="No se han encontrado valores parecidos en esta columna con este parecido.",
    similar_truncated=lambda shown, total: (
        f"Se muestran los primeros {_es(shown)} de {_es(total)} grupos. Los no mostrados usan el valor sugerido."
    ),
    similar_group_summary=lambda variants, cells: (
        f"{variants} variantes · {'1 celda' if cells == 1 else f'{_es(cells)} celdas'}"
    ),
    similar_choose_value="Unificar como:",
    similar_other="Otro:",
    find_duplicates="Buscar filas duplicadas",
    duplicates_title="Filas duplicadas",
    duplicates_exact="Exactas",
    duplicates_similar="Posibles (parecidas)",
    duplicates_compare="Columnas a comparar (dos filas son duplicadas si coinciden en todas ellas):",
    duplicates_compare_similar=(
        "Columnas a comparar (se puntúa el parecido medio; quita las columnas que siempre son distintas, como los ID):"
    ),
    duplicates_ignore_case="Ignorar mayúsculas/minúsculas y espacios sobrantes",
    duplicates_hint="Las filas con todas las columnas comparadas vacías nunca se consideran duplicadas.",
    duplicates_similar_hint=(
        "Las columnas en las que una de las dos filas está vacía no cuentan, y al menos la mitad de las columnas "
        "comparadas deben tener datos. Los grupos no vienen seleccionados: confirma los que sean duplicados de verdad."
    ),
    duplicates_merge="Combinar filas: rellenar las celdas vacías de la fila conservada con los datos de las eliminadas",
    duplicates_searching="Buscando duplicados...",
    duplicates_no_columns="Selecciona al menos una columna para comparar.",
    duplicates_none="No se han encontrado filas duplicadas.",
    duplicates_group=lambda n: f"{_es(n)} filas iguales",
    duplicates_similar_group=lambda n: f"{_es(n)} filas parecidas",
    duplicates_keep="Conservar",
    duplicates_score="Parecido",
    duplicates_result="Resultado",
    duplicates_conflict="Las filas eliminadas tienen valores distintos aquí; se usa el primero. Revísalo.",
    duplicates_truncated=lambda shown, total: (
        f"Se muestran los primeros {_es(shown)} de {_es(total)} grupos. En los exactos no mostrados se conserva "
        "la primera fila; los posibles no mostrados no se modifican."
    ),
    duplicates_summary=lambda groups, rows: (
        f"{'1 grupo' if groups == 1 else f'{_es(groups)} grupos'} · "
        f"se {'eliminará 1 fila' if rows == 1 else f'eliminarán {_es(rows)} filas'}"
    ),
    duplicates_filled=lambda n: "se rellenará 1 celda vacía" if n == 1 else f"se rellenarán {_es(n)} celdas vacías",
    duplicates_remove=lambda n: "Eliminar 1 fila" if n == 1 else f"Eliminar {_es(n)} filas",
    rows_removed=lambda n, filled: (
        f"{'1 fila duplicada eliminada' if n == 1 else f'{_es(n)} filas duplicadas eliminadas'}"
        + (
            f" y {'1 celda vacía rellenada' if filled == 1 else f'{_es(filled)} celdas vacías rellenadas'}"
            if filled
            else ""
        )
        + "."
    ),
    removed_rows=lambda n: "1 fila eliminada" if n == 1 else f"{_es(n)} filas eliminadas",
    export="Exportar",
    export_title="Exportar",
    export_delimiter="Separador de columnas",
    delimiter_names={";": "Punto y coma ( ; ), Excel en español", ",": "Coma ( , ), internacional", "\t": "Tabulador"},
    export_csv_hint="Se guarda en UTF-8 para que las tildes se vean bien en Excel y en bases de datos.",
    export_types_hint=(
        "Elige cómo se guarda cada columna. La sugerencia encaja con todos los valores de la columna; los que no se "
        "pueden convertir sin perder información (007, 1234,56, 13/07/2024...) se guardan como texto."
    ),
    export_column="Columna",
    export_type="Guardar como",
    export_example="Ejemplo",
    export_suggested="sugerido",
    column_type_names={"text": "Texto", "number": "Número", "date": "Fecha", "boolean": "Verdadero/Falso"},
    export_fallbacks=lambda n: (
        "1 valor se quedará como texto" if n == 1 else f"{_es(n)} valores se quedarán como texto"
    ),
    export_error=(
        "No se ha podido guardar el archivo. Comprueba que no esté abierto en otro programa e inténtalo de nuevo."
    ),
    exporting="Guardando...",
    save_as="Guardar como...",
    saved=lambda path: f"Guardado en {path}",
    export_split="Separar filas completas e incompletas",
    export_required="Columnas obligatorias (una fila está completa cuando todas tienen valor):",
    split_counts=lambda complete, incomplete: (
        f"{'1 fila completa' if complete == 1 else f'{_es(complete)} filas completas'} · "
        f"{'1 fila incompleta' if incomplete == 1 else f'{_es(incomplete)} filas incompletas'}"
    ),
    split_single_part="Una de las dos partes está vacía, así que solo se exportará la otra.",
    export_split_csv_hint="Se guardan dos archivos junto al nombre que elijas, terminados en _complete y _incomplete.",
    export_split_xlsx_hint="Un archivo Excel con dos hojas: «Completas» e «Incompletas».",
    sheet_complete="Completas",
    sheet_incomplete="Incompletas",
    history="Historial",
    history_title=lambda steps: f"Historial ({'1 paso' if steps == 1 else f'{_es(steps)} pasos'})",
    history_import=lambda file: f"Importar «{file}»",
    history_cells=lambda action, column, count: (
        f"{action} en «{column}» ({'1 celda' if count == 1 else f'{_es(count)} celdas'})"
    ),
    history_remove_exact=lambda n, filled: (
        f"Eliminar duplicados exactos ({'1 fila' if n == 1 else f'{_es(n)} filas'}"
        + (f", {_es(filled)} rellenadas" if filled else "")
        + ")"
    ),
    history_remove_similar=lambda n, filled: (
        f"Eliminar posibles duplicados ({'1 fila' if n == 1 else f'{_es(n)} filas'}"
        + (f", {_es(filled)} rellenadas" if filled else "")
        + ")"
    ),
    history_hint="Haz doble clic en un paso, o selecciónalo y pulsa el botón, para volver a él.",
    history_go_to="Ir a este paso",
    profile_save_label="Guardar los pasos como perfil de limpieza",
    profile_default_name="Mi perfil de limpieza",
    profile_save=lambda n: "Guardar perfil (1 paso)" if n == 1 else f"Guardar perfil ({_es(n)} pasos)",
    profile_not_replayable=lambda n: (
        f"{'1 paso no se puede' if n == 1 else f'{_es(n)} pasos no se pueden'} guardar en un perfil "
        "(los posibles duplicados necesitan que una persona los confirme)."
    ),
    profile_save_hint=(
        "Un perfil repite cada paso sobre la columna entera; los cambios rechazados fila a fila no se recuerdan. "
        "En los duplicados se conserva la primera fila. Los perfiles también funcionan en la versión web."
    ),
    profile_saved=lambda path: f"Perfil guardado en {path}",
    load_profile="Aplicar perfil",
    profile_title=lambda name: f"Perfil «{name}»",
    profile_apply_hint=(
        "Antes de aplicar nada se comprueba cada paso con los datos actuales. Cada paso aplicado entra en el "
        "historial, así que se puede deshacer."
    ),
    profile_skipped="Se salta: no existe la columna",
    profile_summary=lambda effective, total: f"{_es(effective)} de {_es(total)} pasos cambiarán datos",
    profile_apply=lambda n: "Aplicar 1 paso" if n == 1 else f"Aplicar {_es(n)} pasos",
    profile_applied=lambda name, n: f"Perfil «{name}» aplicado ({'1 paso' if n == 1 else f'{_es(n)} pasos'}).",
    profile_error={
        "invalid": "Este archivo no es un perfil de DataCleanr.",
        "version": "Este perfil se creó con una versión más nueva de DataCleanr.",
        "step": "El perfil tiene un paso no válido.",
    },
    profile_step_cells=lambda action, column: f"{action} en «{column}»",
    profile_step_map=lambda column, n: (
        f"Sustituir valores en «{column}» ({'1 regla' if n == 1 else f'{_es(n)} reglas'})"
    ),
    profile_step_duplicates=lambda columns: f"Eliminar duplicados exactos comparando {columns}",
    confirm_discard_title="Cambios sin exportar",
    confirm_discard="Tienes cambios sin exportar. ¿Descartarlos?",
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
