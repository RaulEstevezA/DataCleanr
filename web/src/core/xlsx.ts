import type { Dataset } from './dataset.ts'

/** A cell as read from an .xlsx file. */
export type XlsxCell = string | number | boolean | Date | null

export interface XlsxSheet {
  sheet: string
  data: XlsxCell[][]
}

export class EmptySheetError extends Error {}

const pad = (n: number) => String(n).padStart(2, '0')

/**
 * Converts a cell to text, as DataCleanr works on text.
 * Dates use ISO order (unambiguous) and only include the time when there is one.
 */
export function cellToText(value: XlsxCell): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'boolean') return value ? 'TRUE' : 'FALSE'
  if (typeof value === 'number') return String(value)
  if (value instanceof Date) {
    // Excel dates have no time zone: the library returns them as UTC
    const date = `${value.getUTCFullYear()}-${pad(value.getUTCMonth() + 1)}-${pad(value.getUTCDate())}`
    const hasTime = value.getUTCHours() + value.getUTCMinutes() + value.getUTCSeconds() > 0
    return hasTime ? `${date} ${pad(value.getUTCHours())}:${pad(value.getUTCMinutes())}:${pad(value.getUTCSeconds())}` : date
  }
  return value
}

/** Builds a dataset from one sheet: first row is the header, fully empty rows are skipped. */
export function sheetToDataset({ sheet, data }: XlsxSheet, fileName: string): Dataset {
  const textRows = data.map((row) => row.map(cellToText)).filter((row) => row.some((cell) => cell !== ''))
  const [header, ...rows] = textRows
  if (!header) throw new EmptySheetError(sheet)
  const normalizedRows = rows.map((row) => header.map((_, i) => row[i] ?? ''))
  return {
    fileName,
    format: 'xlsx',
    sheet,
    columns: header,
    rows: normalizedRows,
    rowIds: normalizedRows.map((_, i) => i),
    delimiter: ',',
    encoding: 'utf-8',
  }
}
