import type { AmountFormat, DecimalSeparator } from '../core/amount.ts'
import type { DateFormat, DateInputOrder } from '../core/date.ts'
import type { PhoneFormat } from '../core/phone.ts'
import type { TransformId } from '../core/transforms.ts'

const formatEn = (n: number) => n.toLocaleString('en')
const formatEs = (n: number) => n.toLocaleString('es')

const en = {
  tagline: 'Clean, normalize and unify tabular data',
  privacyNotice: 'Processed locally. Your files are never sent to a server.',
  languageLabel: 'Language',
  emptyTitle: 'Import a file to get started',
  emptyDescription: 'Load a CSV file to preview its data, pick a column and clean it.',
  importButton: 'Select CSV file',
  importLoading: 'Reading file...',
  importHint: 'or drag and drop it here',
  importAnother: 'Import another file',
  findDuplicates: 'Find duplicate rows',
  removedRows: (n: number) => (n === 1 ? '1 row removed' : `${formatEn(n)} rows removed`),
  rowsRemoved: (n: number) => (n === 1 ? '1 duplicate row removed.' : `${formatEn(n)} duplicate rows removed.`),
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
  duplicatesKeepRow: (row: number) => `Keep row ${formatEn(row)}`,
  duplicatesTruncated: (shown: number, total: number) =>
    `Showing the first ${formatEn(shown)} of ${formatEn(total)} groups. Hidden groups keep their first row.`,
  duplicatesSummary: (groups: number, rows: number) =>
    `${groups === 1 ? '1 group' : `${formatEn(groups)} groups`} · ${rows === 1 ? '1 row' : `${formatEn(rows)} rows`} will be removed`,
  duplicatesRemove: (n: number) => (n === 1 ? 'Remove 1 row' : `Remove ${formatEn(n)} rows`),
  exportCsv: 'Export clean CSV',
  modifiedCells: (n: number) => (n === 1 ? '1 cell modified' : `${formatEn(n)} cells modified`),
  confirmDiscard: 'You have changes that have not been exported. Discard them and import another file?',
  errorNotCsv: 'Only CSV files are supported for now.',
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
  privacyNotice: 'Procesado en local. Tus archivos nunca se envían a ningún servidor.',
  languageLabel: 'Idioma',
  emptyTitle: 'Importa un archivo para empezar',
  emptyDescription: 'Carga un archivo CSV para ver sus datos, elegir una columna y limpiarla.',
  importButton: 'Seleccionar archivo CSV',
  importLoading: 'Leyendo archivo...',
  importHint: 'o arrástralo aquí',
  importAnother: 'Importar otro archivo',
  findDuplicates: 'Buscar filas duplicadas',
  removedRows: (n: number) => (n === 1 ? '1 fila eliminada' : `${formatEs(n)} filas eliminadas`),
  rowsRemoved: (n: number) => (n === 1 ? '1 fila duplicada eliminada.' : `${formatEs(n)} filas duplicadas eliminadas.`),
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
  duplicatesKeepRow: (row: number) => `Conservar la fila ${formatEs(row)}`,
  duplicatesTruncated: (shown: number, total: number) =>
    `Se muestran los primeros ${formatEs(shown)} de ${formatEs(total)} grupos. En los no mostrados se conserva la primera fila.`,
  duplicatesSummary: (groups: number, rows: number) =>
    `${groups === 1 ? '1 grupo' : `${formatEs(groups)} grupos`} · se ${rows === 1 ? 'eliminará 1 fila' : `eliminarán ${formatEs(rows)} filas`}`,
  duplicatesRemove: (n: number) => (n === 1 ? 'Eliminar 1 fila' : `Eliminar ${formatEs(n)} filas`),
  exportCsv: 'Exportar CSV limpio',
  modifiedCells: (n: number) => (n === 1 ? '1 celda modificada' : `${formatEs(n)} celdas modificadas`),
  confirmDiscard: 'Tienes cambios sin exportar. ¿Descartarlos e importar otro archivo?',
  errorNotCsv: 'De momento solo se admiten archivos CSV.',
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
