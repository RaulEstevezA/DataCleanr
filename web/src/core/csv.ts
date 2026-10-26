import Papa from 'papaparse'
import type { Dataset } from './dataset.ts'

export class CsvParseError extends Error {}

// Byte order mark: lets Excel detect UTF-8 so accents display correctly
const UTF8_BOM = '﻿'

/** Parses CSV text. The delimiter is auto-detected and values are kept exactly as written. */
export function parseCsvText(text: string, fileName: string): Dataset {
  const { data, meta } = Papa.parse<string[]>(text.replace(/^﻿/, ''), { skipEmptyLines: 'greedy' })
  const [header, ...rows] = data
  if (!header) throw new CsvParseError('empty')
  // Pad or trim each row so every row has exactly one cell per column
  const normalizedRows = rows.map((row) => header.map((_, i) => row[i] ?? ''))
  return { fileName, columns: header, rows: normalizedRows, delimiter: meta.delimiter }
}

/** Reads and parses a CSV file entirely in the browser. */
export async function parseCsvFile(file: File): Promise<Dataset> {
  return parseCsvText(await file.text(), file.name)
}

/** Serializes the dataset back to CSV using its original delimiter. */
export function serializeCsv(dataset: Dataset): string {
  return (
    UTF8_BOM +
    Papa.unparse({ fields: dataset.columns, data: dataset.rows }, { delimiter: dataset.delimiter, newline: '\r\n' })
  )
}

/** "clientes.csv" -> "clientes_clean.csv" */
export function cleanFileName(fileName: string): string {
  return fileName.replace(/(\.csv)?$/i, '_clean.csv')
}
