/**
 * In-memory table loaded from a file. Rows are kept as arrays (not objects)
 * so column order is preserved and duplicate header names are allowed.
 */
import type { TextEncodingName } from './encoding.ts'

export interface Dataset {
  fileName: string
  /** Header names exactly as they appear in the file (may be empty). */
  columns: string[]
  rows: string[][]
  /** Position of each row in the imported file (0-based). Stays stable when rows are removed. */
  rowIds: number[]
  /** Delimiter detected on import, reused on export. */
  delimiter: string
  /** Encoding detected on import. Export is always UTF-8. */
  encoding: TextEncodingName
}

/** Name to display for a column; empty headers get a positional fallback. */
export function columnLabel(dataset: Dataset, index: number): string {
  return dataset.columns[index].trim() || `#${index + 1}`
}

/** Row number shown to the user: its line in the imported file (1-based, header excluded). */
export function rowNumber(dataset: Dataset, index: number): number {
  return dataset.rowIds[index] + 1
}

/** Number of cells whose value differs between the original and the current dataset (removed rows not counted). */
export function countModifiedCells(original: Dataset, current: Dataset): number {
  let count = 0
  current.rows.forEach((row, r) => {
    const originalRow = original.rows[current.rowIds[r]]
    row.forEach((cell, c) => {
      if (cell !== originalRow[c]) count++
    })
  })
  return count
}

/** Returns a new dataset without the rows at the given indexes. The input dataset is never mutated. */
export function removeRows(dataset: Dataset, indexes: Set<number>): Dataset {
  if (indexes.size === 0) return dataset
  const keep = (_: unknown, i: number) => !indexes.has(i)
  return { ...dataset, rows: dataset.rows.filter(keep), rowIds: dataset.rowIds.filter(keep) }
}
