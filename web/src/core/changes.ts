import type { Dataset } from './dataset.ts'

/** A proposed edit to one cell: shown to the user as "original -> proposed" before applying. */
export interface CellChange {
  row: number
  original: string
  proposed: string
}

/** Runs `transform` over a column and returns only the cells whose value would change. */
export function previewColumnChanges(
  dataset: Dataset,
  column: number,
  transform: (value: string) => string,
): CellChange[] {
  const changes: CellChange[] = []
  dataset.rows.forEach((row, index) => {
    const original = row[column]
    const proposed = transform(original)
    if (proposed !== original) changes.push({ row: index, original, proposed })
  })
  return changes
}

/** Returns a new dataset with the changes applied. The input dataset is never mutated. */
export function applyColumnChanges(dataset: Dataset, column: number, changes: CellChange[]): Dataset {
  if (changes.length === 0) return dataset
  const rows = [...dataset.rows]
  for (const { row, proposed } of changes) {
    const updated = [...rows[row]]
    updated[column] = proposed
    rows[row] = updated
  }
  return { ...dataset, rows }
}
