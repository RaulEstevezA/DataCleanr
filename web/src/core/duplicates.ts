import { comparisonKey, similarity } from './similar.ts'

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

export interface SimilarRowsOptions {
  columns: number[]
  /** Minimum average similarity (0-100) for two rows to be possible duplicates. */
  threshold: number
  ignoreLegalForms: boolean
}

export interface SimilarRowsGroup {
  /** Row indexes, ascending. The first one is the group's reference row. */
  rows: number[]
  /** Similarity of each row to the reference row (the reference itself scores 100). */
  scores: number[]
}

interface CellKey {
  text: string
  /** Character counts: a-z, 0-9, and one shared bucket for anything else. */
  histogram: Uint16Array
}

const HISTOGRAM_SIZE = 37

function toCellKey(text: string): CellKey {
  const histogram = new Uint16Array(HISTOGRAM_SIZE)
  for (let i = 0; i < text.length; i++) {
    const code = text.charCodeAt(i)
    if (code >= 97 && code <= 122) histogram[code - 97]++
    else if (code >= 48 && code <= 57) histogram[code - 48 + 26]++
    else histogram[36]++
  }
  return { text, histogram }
}

/**
 * Cheap upper bound of `similarity`: the common subsequence can never be longer
 * than the characters both texts share. Lets us skip most of the expensive comparisons.
 */
function similarityUpperBound(a: CellKey, b: CellKey): number {
  let shared = 0
  for (let i = 0; i < HISTOGRAM_SIZE; i++) shared += Math.min(a.histogram[i], b.histogram[i])
  return (200 * shared) / (a.text.length + b.text.length)
}

/**
 * Average similarity of two rows over the compared columns, using the same key and
 * score as similar-value grouping. Columns where either cell is empty are skipped
 * (missing data says nothing), and at least half of the columns must be comparable.
 * Returns null when the rows cannot be compared, and 0 as soon as the threshold
 * is out of reach (the exact score is only needed above the threshold).
 */
function rowSimilarity(a: CellKey[], b: CellKey[], threshold: number): number | null {
  const comparable: number[] = []
  let bound = 0
  for (let c = 0; c < a.length; c++) {
    if (a[c].text === '' || b[c].text === '') continue
    comparable.push(c)
    bound += similarityUpperBound(a[c], b[c])
  }
  if (comparable.length === 0 || comparable.length < Math.ceil(a.length / 2)) return null
  const needed = threshold * comparable.length
  if (bound < needed) return 0

  let total = 0
  for (const c of comparable) {
    const score = similarity(a[c].text, b[c].text)
    // Replace this column's bound with its real score: if even that cannot reach the threshold, stop
    bound += score - similarityUpperBound(a[c], b[c])
    if (bound < needed) return 0
    total += score
  }
  return total / comparable.length
}

/**
 * Finds rows that are probably the same record written differently.
 * Greedy, in row order: each row joins the first group whose reference row is at
 * least `threshold` similar, otherwise it starts a new group. Only groups with two
 * or more rows are returned.
 */
export function findSimilarRows(
  rows: string[][],
  { columns, threshold, ignoreLegalForms }: SimilarRowsOptions,
): SimilarRowsGroup[] {
  if (columns.length === 0) return []
  // Comparison keys of the compared columns; blank cells become ''
  const keys = rows.map((row) =>
    columns.map((column) => toCellKey(row[column].trim() === '' ? '' : comparisonKey(row[column], ignoreLegalForms))),
  )

  const groups: SimilarRowsGroup[] = []
  keys.forEach((key, index) => {
    if (key.every((cell) => cell.text === '')) return
    for (const group of groups) {
      const score = rowSimilarity(keys[group.rows[0]], key, threshold)
      if (score !== null && score >= threshold) {
        group.rows.push(index)
        group.scores.push(score)
        return
      }
    }
    groups.push({ rows: [index], scores: [100] })
  })
  return groups.filter((group) => group.rows.length > 1)
}
