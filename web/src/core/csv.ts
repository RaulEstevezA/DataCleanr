import Papa from 'papaparse'
import type { Dataset } from './dataset.ts'

export class CsvParseError extends Error {}

/** Parses a CSV file entirely in the browser. The delimiter is auto-detected. */
export function parseCsvFile(file: File): Promise<Dataset> {
  return new Promise((resolve, reject) => {
    Papa.parse<string[]>(file, {
      skipEmptyLines: 'greedy',
      complete: ({ data }) => {
        const [header, ...rows] = data
        if (!header) {
          reject(new CsvParseError('empty'))
          return
        }
        const columns = header.map((name, i) => name.trim() || `Column ${i + 1}`)
        // Pad or trim each row so every row has exactly one cell per column
        const normalizedRows = rows.map((row) =>
          columns.map((_, i) => row[i] ?? ''),
        )
        resolve({ fileName: file.name, columns, rows: normalizedRows })
      },
      error: (error) => reject(new CsvParseError(error.message)),
    })
  })
}
