export interface DuplicateOptions {
  /** Indexes of the columns to compare. */
  columns: number[]
  /** Treat "TRANSGRAU " and "transgrau" as equal: lowercase, trim and collapse inner spaces. */
  ignoreCaseAndSpaces: boolean
}

// A character that cannot appear in CSV text values, so "ab"+"c" never equals "a"+"bc"
const SEPARATOR = '\u0000'

/**
 * Finds rows with the same values in the compared columns.
 * Returns groups of row indexes (ascending), ordered by their first row.
 * Rows whose compared cells are all empty are ignored: missing data is not a duplicate.
 */
export function findDuplicateRows(rows: string[][], { columns, ignoreCaseAndSpaces }: DuplicateOptions): number[][] {
  if (columns.length === 0) return []
  const normalize = (value: string) => (ignoreCaseAndSpaces ? value.trim().replace(/\s+/g, ' ').toLowerCase() : value)

  const groups = new Map<string, number[]>()
  rows.forEach((row, index) => {
    const cells = columns.map((column) => normalize(row[column]))
    if (cells.every((cell) => cell.trim() === '')) return
    const key = cells.join(SEPARATOR)
    const group = groups.get(key)
    if (group) group.push(index)
    else groups.set(key, [index])
  })

  // Map keeps insertion order, so groups are already ordered by their first row
  return [...groups.values()].filter((group) => group.length > 1)
}
