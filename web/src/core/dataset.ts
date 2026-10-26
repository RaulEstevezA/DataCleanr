/**
 * In-memory table loaded from a file. Rows are kept as arrays (not objects)
 * so column order is preserved and duplicate header names are allowed.
 */
export interface Dataset {
  fileName: string
  columns: string[]
  rows: string[][]
}
