import type { AmountFormat, DecimalSeparator } from '../core/amount.ts'
import type { ColumnType } from '../core/export.ts'
import type { DateFormat, DateInputOrder } from '../core/date.ts'
import type { PhoneFormat } from '../core/phone.ts'
import type { TransformId } from '../core/transforms.ts'

const formatEn = (n: number) => n.toLocaleString('en')
const formatEs = (n: number) => n.toLocaleString('es')

const en = {
  tagline: 'Clean, normalize and unify tabular data',
  privacyShort: 'Processed locally',
  introDescription:
    'Load a messy file, review every change as original → proposed and export clean data: trims, case, phone numbers, dates, amounts, different spellings of the same value (Raúl Estévez / RAUL ESTEVEZ / raul estévez) and duplicate rows.',
  introPrivacyTitle: 'Your data never leaves this browser',
  introPrivacyPoints: [
    'Files are read and processed on your device. There is no server and nothing is uploaded.',
    'Nothing changes without your confirmation, and every step can be undone.',
    'The original file is never modified: you download a cleaned copy.',
  ],
  introCode: 'Source code',
  introDownload: 'Download for desktop',
  introDownloadFor: (platform: string) => `Download for ${platform}`,
  introOtherPlatforms: 'Other platforms',
  introDownloadNote: 'Desktop version for Windows, macOS and Linux (tested on macOS). It is not signed, so the first time your system will show a warning.',
  introHowToOpen: 'How to open it',
  introHowToOpenUrl: 'https://github.com/RaulEstevezA/DataCleanr/blob/main/desktop/README_en.md#opening-it-the-first-time',
  introAllTools: 'All tools',
  languageLabel: 'Language',
  emptyTitle: 'Import a file to get started',
  emptyDescription: 'Load a CSV, Excel (.xlsx), JSON or XML file to preview its data, pick a column and clean it.',
  importButton: 'Select file',
  importLoading: 'Reading file...',
  importHint: 'or drag and drop it here',
  importAnother: 'Import another file',
  findDuplicates: 'Find duplicate rows',
  loadProfile: 'Apply profile',
  profileTitle: (name: string) => `Profile “${name}”`,
  profileApplyHint:
    'Each step is checked against the current data before applying anything. Every applied step is added to the history, so it can be undone.',
  profileSkipped: { missingColumn: 'Skipped: column not found', unavailable: 'Skipped: not available' },
  profileSummary: (effective: number, total: number) => `${formatEn(effective)} of ${formatEn(total)} steps will change data`,
  profileApply: (n: number) => (n === 1 ? 'Apply 1 step' : `Apply ${formatEn(n)} steps`),
  profileApplied: (name: string, n: number) => `Profile “${name}” applied (${n === 1 ? '1 step' : `${formatEn(n)} steps`}).`,
  profileError: {
    invalid: () => 'This file is not a DataCleanr profile.',
    version: () => 'This profile was created with a newer version of DataCleanr.',
    step: (n: number) => `The profile has an invalid step (step ${formatEn(n)}).`,
  },
  profileSaveLabel: 'Profile name',
  profileDefaultName: 'My cleaning profile',
  profileSave: (n: number) => (n === 1 ? 'Save profile (1 step)' : `Save profile (${formatEn(n)} steps)`),
  profileNotReplayable: (n: number) =>
    n === 1
      ? '1 step cannot be saved in a profile (possible duplicates need a person to confirm them).'
      : `${formatEn(n)} steps cannot be saved in a profile (possible duplicates need a person to confirm them).`,
  profileSaveHint:
    'A profile repeats each step on a whole column; changes rejected row by row are not remembered. Duplicates keep the first row.',
  profileStepCells: (action: string, column: string) => `${action} in “${column}”`,
  profileStepMap: (column: string, n: number) => `Replace values in “${column}” (${n === 1 ? '1 rule' : `${formatEn(n)} rules`})`,
  profileStepDuplicates: (columns: string) => `Remove exact duplicates comparing ${columns}`,
  undo: 'Undo',
  redo: 'Redo',
  undoShortcut: 'Undo (Ctrl/Cmd+Z)',
  redoShortcut: 'Redo (Ctrl/Cmd+Shift+Z)',
  historyTitle: (steps: number) => `History (${steps === 1 ? '1 step' : `${formatEn(steps)} steps`})`,
  historyImport: (file: string) => `Import “${file}”`,
  historyCells: (action: string, column: string, count: number) =>
    `${action} in “${column}” (${count === 1 ? '1 cell' : `${formatEn(count)} cells`})`,
  historyRemoveExact: (n: number, filled: number) =>
    `Remove exact duplicates (${n === 1 ? '1 row' : `${formatEn(n)} rows`}${filled > 0 ? `, ${formatEn(filled)} filled` : ''})`,
  historyRemoveSimilar: (n: number, filled: number) =>
    `Remove possible duplicates (${n === 1 ? '1 row' : `${formatEn(n)} rows`}${filled > 0 ? `, ${formatEn(filled)} filled` : ''})`,
  historyHint: 'Click a step to go back to it. Applying a new change discards the steps after it.',
  removedRows: (n: number) => (n === 1 ? '1 row removed' : `${formatEn(n)} rows removed`),
  rowsRemoved: (n: number, filled: number) =>
    `${n === 1 ? '1 duplicate row removed' : `${formatEn(n)} duplicate rows removed`}${
      filled > 0 ? ` and ${filled === 1 ? '1 empty cell' : `${formatEn(filled)} empty cells`} filled` : ''
    }.`,
  close: 'Close',
  duplicatesTitle: 'Duplicate rows',
  duplicatesMode: 'Kind of duplicates',
  duplicatesExact: 'Exact',
  duplicatesSimilar: 'Possible (similar)',
  duplicatesCompareSimilar:
    'Columns to compare (rows are scored by their average similarity; leave out columns that are always different, like IDs):',
  duplicatesSimilarHint:
    'Columns where one of the two rows is empty are skipped, and at least half of the compared columns must have data. Groups are not selected by default: confirm the ones that are real duplicates.',
  duplicatesSimilarGroup: (n: number) => `${formatEn(n)} similar rows`,
  duplicatesScore: 'Similarity',
  duplicatesSimilarTruncated: (shown: number, total: number) =>
    `Showing the first ${formatEn(shown)} of ${formatEn(total)} groups. Hidden groups are not modified.`,
  duplicatesTooManyRows: (rows: number, max: number) =>
    `The file has ${formatEn(rows)} rows. Possible-duplicate detection supports up to ${formatEn(max)} for now.`,
  duplicatesCompare: 'Columns to compare (two rows are duplicates if they match in all of them):',
  duplicatesIgnoreCase: 'Ignore upper/lower case and extra spaces',
  duplicatesHint: 'Rows with all compared columns empty are never treated as duplicates.',
  duplicatesNoColumns: 'Select at least one column to compare.',
  duplicatesNone: 'No duplicate rows found.',
  duplicatesGroup: (n: number) => `${formatEn(n)} identical rows`,
  duplicatesKeep: 'Keep',
  duplicatesMerge: 'Combine rows: fill empty cells of the kept row with data from the removed ones',
  duplicatesResult: 'Result',
  duplicatesConflict: 'The removed rows have different values here; the first one is used. Check it.',
  duplicatesFilled: (n: number) => (n === 1 ? '1 empty cell will be filled' : `${formatEn(n)} empty cells will be filled`),
  duplicatesKeepRow: (row: number) => `Keep row ${formatEn(row)}`,
  duplicatesTruncated: (shown: number, total: number) =>
    `Showing the first ${formatEn(shown)} of ${formatEn(total)} groups. Hidden groups keep their first row.`,
  duplicatesSummary: (groups: number, rows: number) =>
    `${groups === 1 ? '1 group' : `${formatEn(groups)} groups`} · ${rows === 1 ? '1 row' : `${formatEn(rows)} rows`} will be removed`,
  duplicatesRemove: (n: number) => (n === 1 ? 'Remove 1 row' : `Remove ${formatEn(n)} rows`),
  exportCsv: 'Export',
  exportTitle: 'Export',
  exportFormat: 'File format',
  exportDelimiter: 'Column separator',
  delimiterNames: { ';': 'Semicolon ( ; ), Excel in Spanish', ',': 'Comma ( , ), international', '\t': 'Tab' },
  exportCsvHint: 'Saved as UTF-8 so accents display correctly in Excel and databases.',
  exportTypesHint:
    'Choose how each column is saved. The suggestion fits every value of the column; values that cannot be converted without losing information (007, 1234,56, 13/07/2024...) are saved as text.',
  exportColumn: 'Column',
  exportType: 'Save as',
  exportExample: 'Example',
  exportTypeOf: (column: string) => `Type of “${column}”`,
  exportSuggested: 'suggested',
  columnTypeNames: { text: 'Text', number: 'Number', date: 'Date', boolean: 'True/False' } satisfies Record<ColumnType, string>,
  exportFallbacks: (n: number) => (n === 1 ? '1 value will stay as text' : `${formatEn(n)} values will stay as text`),
  exportError: 'The file could not be created. Try again.',
  exportSplit: 'Separate complete and incomplete rows',
  exportRequired: 'Required columns (a row is complete when all of them have a value):',
  splitCounts: (complete: number, incomplete: number) =>
    `${complete === 1 ? '1 complete row' : `${formatEn(complete)} complete rows`} · ${
      incomplete === 1 ? '1 incomplete row' : `${formatEn(incomplete)} incomplete rows`
    }`,
  splitSinglePart: 'One of the parts is empty, so only the other one will be exported.',
  exportSplitCsvHint: 'Two files are downloaded. Your browser may ask for permission to download several files.',
  exportSplitXlsxHint: 'One Excel file with two sheets: “Complete” and “Incomplete”.',
  sheetComplete: 'Complete',
  sheetIncomplete: 'Incomplete',
  exporting: 'Creating file...',
  download: 'Download',
  modifiedCells: (n: number) => (n === 1 ? '1 cell modified' : `${formatEn(n)} cells modified`),
  confirmDiscard: 'You have changes that have not been exported. Discard them and import another file?',
  errorUnsupported: 'Only CSV, Excel (.xlsx), JSON and XML files are supported.',
  errorParseXml: {
    invalid: 'The file is not well-formed XML.',
    unsupported: 'No repeated elements were found to use as rows in this XML.',
  },
  errorParseJson: {
    invalid: 'The file is not valid JSON.',
    unsupported:
      'This JSON does not look like a table. Supported: a list of objects, a list of lists, or an object holding one of those lists.',
    empty: 'The JSON list is empty.',
  },
  errorOldExcel: 'The old Excel format (.xls) is not supported. Open it in Excel and save it as .xlsx.',
  errorParseExcel: 'The Excel file could not be read, or all its sheets are empty.',
  sheet: 'Sheet',
  emptySheet: (sheet: string) => `The sheet “${sheet}” is empty.`,
  confirmDiscardSheet: 'You have changes that have not been exported. Discard them and open another sheet?',
  errorParse: 'The file could not be read. Check that it is a valid, non-empty CSV.',
  rowCount: (n: number) => (n === 1 ? '1 row' : `${formatEn(n)} rows`),
  columnCount: (n: number) => (n === 1 ? '1 column' : `${formatEn(n)} columns`),
  detectedColumns: 'Detected columns',
  emptyCell: 'empty',
  pagination: 'Pagination',
  previous: 'Previous',
  next: 'Next',
  rowRange: (from: number, to: number, total: number) => `Rows ${formatEn(from)}–${formatEn(to)} of ${formatEn(total)}`,
  cleanColumn: (column: string) => `Clean column “${column}”`,
  transformLabel: 'Transformation',
  transformNames: {
    trim: 'Trim spaces',
    collapseSpaces: 'Collapse repeated spaces',
    lowercase: 'lowercase',
    uppercase: 'UPPERCASE',
    titleCase: 'Title Case',
  } satisfies Record<TransformId, string>,
  customReplace: 'Custom replace',
  findLabel: 'Find',
  replaceLabel: 'Replace with',
  findPlaceholder: 'Text to find',
  replacePlaceholder: 'New value',
  wholeCell: 'Match whole cell',
  ignoreCase: 'Ignore upper/lower case',
  noMatches: 'No cell matches the text you are looking for.',
  normalizePhone: 'Normalize phone numbers',
  phoneCountry: 'Default country (numbers without prefix)',
  phoneFormat: 'Output format',
  phoneFormatNames: {
    E164: 'E.164 (databases)',
    INTERNATIONAL: 'International',
    NATIONAL: 'National',
  } satisfies Record<PhoneFormat, string>,
  phoneHint:
    'Numbers that already have a prefix (+33, +44...) keep their country. In national format, foreign numbers stay international so their country is not lost.',
  phoneLoading: 'Loading phone number rules...',
  phoneLoadError: 'Phone number rules could not be loaded. Check your connection and try again.',
  normalizeIssues: (n: number) =>
    n === 1
      ? '1 value could not be normalized and will be left unchanged. Review it by hand.'
      : `${formatEn(n)} values could not be normalized and will be left unchanged. Review them by hand.`,
  similarValues: 'Unify similar values',
  similarThreshold: (n: number) => `Similarity: ${n}%`,
  similarThresholdHint: 'Lower groups more values (and more false matches); higher is stricter.',
  similarIgnoreLegalForms: 'Ignore legal forms when comparing (S.L., S.A., Inc...)',
  similarNone: 'No similar values found in this column with this similarity.',
  similarGroupSummary: (variants: number, cells: number) =>
    `${variants} variants · ${cells === 1 ? '1 cell' : `${formatEn(cells)} cells`}`,
  similarChooseValue: 'Unify as:',
  similarOther: 'Other:',
  similarTooMany: (distinct: number, max: number) =>
    `This column has ${formatEn(distinct)} different values. Similar-value grouping supports up to ${formatEn(max)} for now.`,
  normalizeAmount: 'Normalize amounts',
  amountAmbiguous: 'Decimal separator when in doubt (e.g. 1.234)',
  amountSeparatorNames: {
    ',': 'Comma',
    '.': 'Dot',
  } satisfies Record<DecimalSeparator, string>,
  amountFormat: 'Output format',
  amountFormatNames: {
    DOT: 'Dot decimal (databases)',
    COMMA: 'Comma decimal',
    COMMA_GROUPED: 'Spanish style',
    DOT_GROUPED: 'English style',
  } satisfies Record<AmountFormat, string>,
  amountTwoDecimals: 'Always two decimals (never rounded: extra decimals go to review)',
  amountHint:
    'Unambiguous values are detected automatically: 12063.99 and 5837,32 are decimals, 1.234.567 is thousands. Currency symbols (€, $, £, EUR...) are removed.',
  amountMixedCurrencies: (list: string) =>
    `This column mixes currencies (${list}). Removing the symbols loses that information: review before applying.`,
  normalizeDate: 'Normalize dates',
  dateInputOrder: 'How are dates written in this column?',
  dateOrderNames: {
    DMY: 'Day / month / year',
    MDY: 'Month / day / year',
  } satisfies Record<DateInputOrder, string>,
  dateFormat: 'Output format',
  dateFormatNames: {
    ISO: 'ISO 8601 (databases)',
    DMY: 'DD/MM/YYYY',
    MDY: 'MM/DD/YYYY',
  } satisfies Record<DateFormat, string>,
  dateTwoDigitLimit: 'Two-digit years: up to which year are they 2000s? (Excel uses 29)',
  dateHint: 'Dates starting with the year (2024-07-13) are always read as year-month-day.',
  noChanges: 'Nothing to change: this column is already clean for this transformation.',
  original: 'Original',
  proposed: 'Proposed',
  toggleAll: 'Accept or reject all changes',
  acceptRow: (row: number) => `Accept change in row ${formatEn(row)}`,
  previewTruncated: (shown: number, total: number) =>
    `Showing the first ${formatEn(shown)} of ${formatEn(total)} changes. Hidden changes are accepted.`,
  changesSelected: (accepted: number, total: number) =>
    `${formatEn(accepted)} of ${formatEn(total)} ${total === 1 ? 'change' : 'changes'} selected`,
  cancel: 'Cancel',
  applyChanges: (n: number) => (n === 1 ? 'Apply 1 change' : `Apply ${formatEn(n)} changes`),
  changesApplied: (n: number, column: string) =>
    n === 1 ? `1 change applied to “${column}”.` : `${formatEn(n)} changes applied to “${column}”.`,
  license: 'MIT License',
  sourceCode: 'Source code',
}

export type Messages = typeof en

const es: Messages = {
  tagline: 'Limpia, normaliza y unifica datos tabulares',
  privacyShort: 'Procesado en local',
  introDescription:
    'Carga un archivo sucio, revisa cada cambio como original → propuesto y exporta los datos limpios: espacios, mayúsculas, teléfonos, fechas, importes, distintas formas de escribir lo mismo (Raúl Estévez / RAUL ESTEVEZ / raul estévez) y filas duplicadas.',
  introPrivacyTitle: 'Tus datos no salen de este navegador',
  introPrivacyPoints: [
    'Los archivos se leen y se procesan en tu dispositivo. No hay servidor y no se sube nada.',
    'Nada cambia sin tu confirmación, y cualquier paso se puede deshacer.',
    'El archivo original nunca se modifica: descargas una copia limpia.',
  ],
  introCode: 'Código fuente',
  introDownload: 'Descargar para escritorio',
  introDownloadFor: (platform: string) => `Descargar para ${platform}`,
  introOtherPlatforms: 'Otras plataformas',
  introDownloadNote: 'Versión de escritorio para Windows, macOS y Linux (probada en macOS). No está firmada, así que la primera vez el sistema mostrará un aviso.',
  introHowToOpen: 'Cómo abrirla',
  introHowToOpenUrl: 'https://github.com/RaulEstevezA/DataCleanr/blob/main/desktop/README_es.md#abrirla-la-primera-vez',
  introAllTools: 'Todas las herramientas',
  languageLabel: 'Idioma',
  emptyTitle: 'Importa un archivo para empezar',
  emptyDescription: 'Carga un archivo CSV, Excel (.xlsx), JSON o XML para ver sus datos, elegir una columna y limpiarla.',
  importButton: 'Seleccionar archivo',
  importLoading: 'Leyendo archivo...',
  importHint: 'o arrástralo aquí',
  importAnother: 'Importar otro archivo',
  findDuplicates: 'Buscar filas duplicadas',
  loadProfile: 'Aplicar perfil',
  profileTitle: (name: string) => `Perfil «${name}»`,
  profileApplyHint:
    'Antes de aplicar nada se comprueba cada paso con los datos actuales. Cada paso aplicado entra en el historial, así que se puede deshacer.',
  profileSkipped: { missingColumn: 'Se salta: no existe la columna', unavailable: 'Se salta: no disponible' },
  profileSummary: (effective: number, total: number) => `${formatEs(effective)} de ${formatEs(total)} pasos cambiarán datos`,
  profileApply: (n: number) => (n === 1 ? 'Aplicar 1 paso' : `Aplicar ${formatEs(n)} pasos`),
  profileApplied: (name: string, n: number) => `Perfil «${name}» aplicado (${n === 1 ? '1 paso' : `${formatEs(n)} pasos`}).`,
  profileError: {
    invalid: () => 'Este archivo no es un perfil de DataCleanr.',
    version: () => 'Este perfil se creó con una versión más nueva de DataCleanr.',
    step: (n: number) => `El perfil tiene un paso no válido (paso ${formatEs(n)}).`,
  },
  profileSaveLabel: 'Nombre del perfil',
  profileDefaultName: 'Mi perfil de limpieza',
  profileSave: (n: number) => (n === 1 ? 'Guardar perfil (1 paso)' : `Guardar perfil (${formatEs(n)} pasos)`),
  profileNotReplayable: (n: number) =>
    n === 1
      ? '1 paso no se puede guardar en un perfil (los posibles duplicados necesitan que una persona los confirme).'
      : `${formatEs(n)} pasos no se pueden guardar en un perfil (los posibles duplicados necesitan que una persona los confirme).`,
  profileSaveHint:
    'Un perfil repite cada paso sobre la columna entera; los cambios rechazados fila a fila no se recuerdan. En los duplicados se conserva la primera fila.',
  profileStepCells: (action: string, column: string) => `${action} en «${column}»`,
  profileStepMap: (column: string, n: number) => `Sustituir valores en «${column}» (${n === 1 ? '1 regla' : `${formatEs(n)} reglas`})`,
  profileStepDuplicates: (columns: string) => `Eliminar duplicados exactos comparando ${columns}`,
  undo: 'Deshacer',
  redo: 'Rehacer',
  undoShortcut: 'Deshacer (Ctrl/Cmd+Z)',
  redoShortcut: 'Rehacer (Ctrl/Cmd+Mayús+Z)',
  historyTitle: (steps: number) => `Historial (${steps === 1 ? '1 paso' : `${formatEs(steps)} pasos`})`,
  historyImport: (file: string) => `Importar «${file}»`,
  historyCells: (action: string, column: string, count: number) =>
    `${action} en «${column}» (${count === 1 ? '1 celda' : `${formatEs(count)} celdas`})`,
  historyRemoveExact: (n: number, filled: number) =>
    `Eliminar duplicados exactos (${n === 1 ? '1 fila' : `${formatEs(n)} filas`}${filled > 0 ? `, ${formatEs(filled)} rellenadas` : ''})`,
  historyRemoveSimilar: (n: number, filled: number) =>
    `Eliminar posibles duplicados (${n === 1 ? '1 fila' : `${formatEs(n)} filas`}${filled > 0 ? `, ${formatEs(filled)} rellenadas` : ''})`,
  historyHint: 'Haz clic en un paso para volver a él. Si aplicas un cambio nuevo, se descartan los pasos posteriores.',
  removedRows: (n: number) => (n === 1 ? '1 fila eliminada' : `${formatEs(n)} filas eliminadas`),
  rowsRemoved: (n: number, filled: number) =>
    `${n === 1 ? '1 fila duplicada eliminada' : `${formatEs(n)} filas duplicadas eliminadas`}${
      filled > 0 ? ` y ${filled === 1 ? '1 celda vacía rellenada' : `${formatEs(filled)} celdas vacías rellenadas`}` : ''
    }.`,
  close: 'Cerrar',
  duplicatesTitle: 'Filas duplicadas',
  duplicatesMode: 'Tipo de duplicados',
  duplicatesExact: 'Exactas',
  duplicatesSimilar: 'Posibles (parecidas)',
  duplicatesCompareSimilar:
    'Columnas a comparar (se puntúa el parecido medio; quita las columnas que siempre son distintas, como los ID):',
  duplicatesSimilarHint:
    'Las columnas en las que una de las dos filas está vacía no cuentan, y al menos la mitad de las columnas comparadas deben tener datos. Los grupos no vienen seleccionados: confirma los que sean duplicados de verdad.',
  duplicatesSimilarGroup: (n: number) => `${formatEs(n)} filas parecidas`,
  duplicatesScore: 'Parecido',
  duplicatesSimilarTruncated: (shown: number, total: number) =>
    `Se muestran los primeros ${formatEs(shown)} de ${formatEs(total)} grupos. Los no mostrados no se modifican.`,
  duplicatesTooManyRows: (rows: number, max: number) =>
    `El archivo tiene ${formatEs(rows)} filas. De momento, la detección de posibles duplicados admite hasta ${formatEs(max)}.`,
  duplicatesCompare: 'Columnas a comparar (dos filas son duplicadas si coinciden en todas ellas):',
  duplicatesIgnoreCase: 'Ignorar mayúsculas/minúsculas y espacios sobrantes',
  duplicatesHint: 'Las filas con todas las columnas comparadas vacías nunca se consideran duplicadas.',
  duplicatesNoColumns: 'Selecciona al menos una columna para comparar.',
  duplicatesNone: 'No se han encontrado filas duplicadas.',
  duplicatesGroup: (n: number) => `${formatEs(n)} filas iguales`,
  duplicatesKeep: 'Conservar',
  duplicatesMerge: 'Combinar filas: rellenar las celdas vacías de la fila conservada con los datos de las eliminadas',
  duplicatesResult: 'Resultado',
  duplicatesConflict: 'Las filas eliminadas tienen valores distintos aquí; se usa el primero. Revísalo.',
  duplicatesFilled: (n: number) => (n === 1 ? 'se rellenará 1 celda vacía' : `se rellenarán ${formatEs(n)} celdas vacías`),
  duplicatesKeepRow: (row: number) => `Conservar la fila ${formatEs(row)}`,
  duplicatesTruncated: (shown: number, total: number) =>
    `Se muestran los primeros ${formatEs(shown)} de ${formatEs(total)} grupos. En los no mostrados se conserva la primera fila.`,
  duplicatesSummary: (groups: number, rows: number) =>
    `${groups === 1 ? '1 grupo' : `${formatEs(groups)} grupos`} · se ${rows === 1 ? 'eliminará 1 fila' : `eliminarán ${formatEs(rows)} filas`}`,
  duplicatesRemove: (n: number) => (n === 1 ? 'Eliminar 1 fila' : `Eliminar ${formatEs(n)} filas`),
  exportCsv: 'Exportar',
  exportTitle: 'Exportar',
  exportFormat: 'Formato del archivo',
  exportDelimiter: 'Separador de columnas',
  delimiterNames: { ';': 'Punto y coma ( ; ), Excel en español', ',': 'Coma ( , ), internacional', '\t': 'Tabulador' },
  exportCsvHint: 'Se guarda en UTF-8 para que las tildes se vean bien en Excel y en bases de datos.',
  exportTypesHint:
    'Elige cómo se guarda cada columna. La sugerencia encaja con todos los valores de la columna; los que no se pueden convertir sin perder información (007, 1234,56, 13/07/2024...) se guardan como texto.',
  exportColumn: 'Columna',
  exportType: 'Guardar como',
  exportExample: 'Ejemplo',
  exportTypeOf: (column: string) => `Tipo de «${column}»`,
  exportSuggested: 'sugerido',
  columnTypeNames: { text: 'Texto', number: 'Número', date: 'Fecha', boolean: 'Verdadero/Falso' },
  exportFallbacks: (n: number) => (n === 1 ? '1 valor se quedará como texto' : `${formatEs(n)} valores se quedarán como texto`),
  exportError: 'No se ha podido crear el archivo. Inténtalo de nuevo.',
  exportSplit: 'Separar filas completas e incompletas',
  exportRequired: 'Columnas obligatorias (una fila está completa cuando todas tienen valor):',
  splitCounts: (complete: number, incomplete: number) =>
    `${complete === 1 ? '1 fila completa' : `${formatEs(complete)} filas completas`} · ${
      incomplete === 1 ? '1 fila incompleta' : `${formatEs(incomplete)} filas incompletas`
    }`,
  splitSinglePart: 'Una de las dos partes está vacía, así que solo se exportará la otra.',
  exportSplitCsvHint: 'Se descargan dos archivos. El navegador puede pedirte permiso para descargar varios archivos.',
  exportSplitXlsxHint: 'Un archivo Excel con dos hojas: «Completas» e «Incompletas».',
  sheetComplete: 'Completas',
  sheetIncomplete: 'Incompletas',
  exporting: 'Creando archivo...',
  download: 'Descargar',
  modifiedCells: (n: number) => (n === 1 ? '1 celda modificada' : `${formatEs(n)} celdas modificadas`),
  confirmDiscard: 'Tienes cambios sin exportar. ¿Descartarlos e importar otro archivo?',
  errorUnsupported: 'Solo se admiten archivos CSV, Excel (.xlsx), JSON y XML.',
  errorParseXml: {
    invalid: 'El archivo no es un XML bien formado.',
    unsupported: 'No se han encontrado elementos repetidos que usar como filas en este XML.',
  },
  errorParseJson: {
    invalid: 'El archivo no es un JSON válido.',
    unsupported:
      'Este JSON no parece una tabla. Se admite una lista de objetos, una lista de listas o un objeto que contenga una de esas listas.',
    empty: 'La lista del JSON está vacía.',
  },
  errorOldExcel: 'El formato antiguo de Excel (.xls) no está soportado. Ábrelo en Excel y guárdalo como .xlsx.',
  errorParseExcel: 'No se ha podido leer el archivo Excel, o todas sus hojas están vacías.',
  sheet: 'Hoja',
  emptySheet: (sheet: string) => `La hoja «${sheet}» está vacía.`,
  confirmDiscardSheet: 'Tienes cambios sin exportar. ¿Descartarlos y abrir otra hoja?',
  errorParse: 'No se ha podido leer el archivo. Comprueba que sea un CSV válido y no esté vacío.',
  rowCount: (n: number) => (n === 1 ? '1 fila' : `${formatEs(n)} filas`),
  columnCount: (n: number) => (n === 1 ? '1 columna' : `${formatEs(n)} columnas`),
  detectedColumns: 'Columnas detectadas',
  emptyCell: 'vacío',
  pagination: 'Paginación',
  previous: 'Anterior',
  next: 'Siguiente',
  rowRange: (from: number, to: number, total: number) => `Filas ${formatEs(from)}–${formatEs(to)} de ${formatEs(total)}`,
  cleanColumn: (column: string) => `Limpiar columna «${column}»`,
  transformLabel: 'Transformación',
  transformNames: {
    trim: 'Quitar espacios de los extremos',
    collapseSpaces: 'Quitar espacios repetidos',
    lowercase: 'minúsculas',
    uppercase: 'MAYÚSCULAS',
    titleCase: 'Primera En Mayúscula',
  },
  customReplace: 'Reemplazo personalizado',
  findLabel: 'Buscar',
  replaceLabel: 'Reemplazar por',
  findPlaceholder: 'Texto a buscar',
  replacePlaceholder: 'Nuevo valor',
  wholeCell: 'Coincidir con la celda completa',
  ignoreCase: 'Ignorar mayúsculas/minúsculas',
  noMatches: 'Ninguna celda coincide con el texto buscado.',
  normalizePhone: 'Normalizar teléfonos',
  phoneCountry: 'País por defecto (números sin prefijo)',
  phoneFormat: 'Formato de salida',
  phoneFormatNames: {
    E164: 'E.164 (bases de datos)',
    INTERNATIONAL: 'Internacional',
    NATIONAL: 'Nacional',
  },
  phoneHint:
    'Los números que ya tienen prefijo (+33, +44...) mantienen su país. En formato nacional, los extranjeros se dejan en internacional para no perder su país.',
  phoneLoading: 'Cargando reglas de teléfonos...',
  phoneLoadError: 'No se han podido cargar las reglas de teléfonos. Revisa tu conexión e inténtalo de nuevo.',
  normalizeIssues: (n: number) =>
    n === 1
      ? '1 valor no se puede normalizar y se dejará sin cambios. Revísalo a mano.'
      : `${formatEs(n)} valores no se pueden normalizar y se dejarán sin cambios. Revísalos a mano.`,
  similarValues: 'Unificar valores parecidos',
  similarThreshold: (n: number) => `Parecido: ${n}%`,
  similarThresholdHint: 'Más bajo agrupa más valores (y más falsos parecidos); más alto es más estricto.',
  similarIgnoreLegalForms: 'Ignorar formas jurídicas al comparar (S.L., S.A., Inc...)',
  similarNone: 'No se han encontrado valores parecidos en esta columna con este parecido.',
  similarGroupSummary: (variants: number, cells: number) =>
    `${variants} variantes · ${cells === 1 ? '1 celda' : `${formatEs(cells)} celdas`}`,
  similarChooseValue: 'Unificar como:',
  similarOther: 'Otro:',
  similarTooMany: (distinct: number, max: number) =>
    `Esta columna tiene ${formatEs(distinct)} valores distintos. De momento, la agrupación de parecidos admite hasta ${formatEs(max)}.`,
  normalizeAmount: 'Normalizar importes',
  amountAmbiguous: 'Separador decimal en caso de duda (ej. 1.234)',
  amountSeparatorNames: {
    ',': 'Coma',
    '.': 'Punto',
  },
  amountFormat: 'Formato de salida',
  amountFormatNames: {
    DOT: 'Punto decimal (bases de datos)',
    COMMA: 'Coma decimal',
    COMMA_GROUPED: 'Formato español',
    DOT_GROUPED: 'Formato inglés',
  },
  amountTwoDecimals: 'Siempre dos decimales (nunca redondea: si hay más, van a revisión)',
  amountHint:
    'Los valores sin ambigüedad se detectan solos: 12063.99 y 5837,32 son decimales, 1.234.567 son miles. Se quitan los símbolos de moneda (€, $, £, EUR...).',
  amountMixedCurrencies: (list: string) =>
    `Esta columna mezcla monedas (${list}). Al quitar los símbolos se pierde esa información: revísala antes de aplicar.`,
  normalizeDate: 'Normalizar fechas',
  dateInputOrder: '¿Cómo están escritas las fechas en esta columna?',
  dateOrderNames: {
    DMY: 'Día / mes / año',
    MDY: 'Mes / día / año',
  },
  dateFormat: 'Formato de salida',
  dateFormatNames: {
    ISO: 'ISO 8601 (bases de datos)',
    DMY: 'DD/MM/AAAA',
    MDY: 'MM/DD/AAAA',
  },
  dateTwoDigitLimit: 'Años de dos cifras: ¿hasta qué año son del 2000? (Excel usa el 29)',
  dateHint: 'Las fechas que empiezan por el año (2024-07-13) se leen siempre como año-mes-día.',
  noChanges: 'No hay nada que cambiar: esta columna ya está limpia para esta transformación.',
  original: 'Original',
  proposed: 'Propuesto',
  toggleAll: 'Aceptar o rechazar todos los cambios',
  acceptRow: (row: number) => `Aceptar cambio en la fila ${formatEs(row)}`,
  previewTruncated: (shown: number, total: number) =>
    `Se muestran los primeros ${formatEs(shown)} de ${formatEs(total)} cambios. Los cambios no mostrados se aceptan.`,
  changesSelected: (accepted: number, total: number) =>
    `${formatEs(accepted)} de ${formatEs(total)} ${total === 1 ? 'cambio seleccionado' : 'cambios seleccionados'}`,
  cancel: 'Cancelar',
  applyChanges: (n: number) => (n === 1 ? 'Aplicar 1 cambio' : `Aplicar ${formatEs(n)} cambios`),
  changesApplied: (n: number, column: string) =>
    n === 1 ? `1 cambio aplicado en «${column}».` : `${formatEs(n)} cambios aplicados en «${column}».`,
  license: 'Licencia MIT',
  sourceCode: 'Código fuente',
}

export const messages = { en, es }

export type Language = keyof typeof messages

export const languages = Object.keys(messages) as Language[]
