const en = {
  tagline: 'Clean, normalize and unify tabular data',
  privacyNotice: 'Processed locally. Your files are never sent to a server.',
  languageLabel: 'Language',
  emptyTitle: 'Import a file to get started',
  emptyDescription: 'Load a CSV file to preview its data, pick a column and clean it.',
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
  license: 'Licencia MIT',
  sourceCode: 'Código fuente',
}

export const messages = { en, es }

export type Language = keyof typeof messages

export const languages = Object.keys(messages) as Language[]
