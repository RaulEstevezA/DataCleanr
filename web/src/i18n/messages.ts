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
