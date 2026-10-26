import Papa from 'papaparse'
import type { Dataset } from './dataset.ts'
import { decodeText, type TextEncodingName } from './encoding.ts'

export class CsvParseError extends Error {}

// Byte order mark: lets Excel detect UTF-8 so accents display correctly
const UTF8_BOM = '﻿'

/** Parses CSV text. The delimiter is auto-detected and values are kept exactly as written. */
export function parseCsvText(text: string, fileName: string, encoding: TextEncodingName = 'utf-8'): Dataset {
  const { data, meta } = Papa.parse<string[]>(text.replace(/^﻿/, ''), { skipEmptyLines: 'greedy' })
  const [header, ...rows] = data
  if (!header) throw new CsvParseError('empty')
  // Pad or trim each row so every row has exactly one cell per column
  const normalizedRows = rows.map((row) => header.map((_, i) => row[i] ?? ''))
  return {
    fileName,
    format: 'csv',
    sheet: null,
    columns: header,
    rows: normalizedRows,
    rowIds: normalizedRows.map((_, i) => i),
    delimiter: meta.delimiter,
    encoding,
  }
}

/** Reads and parses a CSV file entirely in the browser, detecting its text encoding. */
export async function parseCsvFile(file: File): Promise<Dataset> {
  const { text, encoding } = decodeText(new Uint8Array(await file.arrayBuffer()))
  return parseCsvText(text, file.name, encoding)
}

/** Serializes the dataset back to CSV using its original delimiter. Always UTF-8, whatever the input encoding. */
export function serializeCsv(dataset: Dataset): string {
  return (
    UTF8_BOM +
    Papa.unparse({ fields: dataset.columns, data: dataset.rows }, { delimiter: dataset.delimiter, newline: '\r\n' })
  )
}

/**
 * "clientes.csv" (or .xlsx, .json, .xml) -> "clientes_clean.csv" (or .xlsx).
 * With a part: "clientes_clean_complete.csv". Suffixes are in English so file names don't depend on the language.
 */
export function cleanFileName(fileName: string, extension: 'csv' | 'xlsx' = 'csv', part?: string): string {
  return fileName.replace(/(\.(csv|xlsx|json|xml))?$/i, `_clean${part ? `_${part}` : ''}.${extension}`)
}
