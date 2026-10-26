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
  /** Delimiter detected on import, reused on export. */
  delimiter: string
  /** Encoding detected on import. Export is always UTF-8. */
  encoding: TextEncodingName
}

/** Name to display for a column; empty headers get a positional fallback. */
export function columnLabel(dataset: Dataset, index: number): string {
  return dataset.columns[index].trim() || `#${index + 1}`
}

/** Number of cells whose value differs between two versions of the same dataset. */
export function countModifiedCells(original: Dataset, current: Dataset): number {
  let count = 0
  current.rows.forEach((row, r) => {
    row.forEach((cell, c) => {
      if (cell !== original.rows[r][c]) count++
    })
  })
  return count
}
