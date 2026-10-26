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
  errorNotCsv: 'Only CSV files are supported for now.',
  errorParse: 'The file could not be read. Check that it is a valid, non-empty CSV.',
  rowCount: (n: string) => `${n} rows`,
  columnCount: (n: string) => `${n} columns`,
  detectedColumns: 'Detected columns',
  emptyCell: 'empty',
  pagination: 'Pagination',
  previous: 'Previous',
  next: 'Next',
  rowRange: (from: string, to: string, total: string) => `Rows ${from}–${to} of ${total}`,
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
  errorNotCsv: 'De momento solo se admiten archivos CSV.',
  errorParse: 'No se ha podido leer el archivo. Comprueba que sea un CSV válido y no esté vacío.',
  rowCount: (n: string) => `${n} filas`,
  columnCount: (n: string) => `${n} columnas`,
  detectedColumns: 'Columnas detectadas',
  emptyCell: 'vacío',
  pagination: 'Paginación',
  previous: 'Anterior',
  next: 'Siguiente',
  rowRange: (from: string, to: string, total: string) => `Filas ${from}–${to} de ${total}`,
  license: 'Licencia MIT',
  sourceCode: 'Código fuente',
}

export const messages = { en, es }

export type Language = keyof typeof messages

export const languages = Object.keys(messages) as Language[]
