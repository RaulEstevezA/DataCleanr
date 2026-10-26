import type { Dataset } from './dataset.ts'

export interface SplitResult {
  /** Rows with a value in every required column. */
  complete: Dataset
  /** Rows with at least one required column empty (whitespace-only counts as empty). */
  incomplete: Dataset
}

/** Indexes of the complete and incomplete rows, in their original order. */
export function splitRowIndexes(rows: string[][], required: number[]): { complete: number[]; incomplete: number[] } {
  const complete: number[] = []
  const incomplete: number[] = []
  rows.forEach((row, index) => {
    const isComplete = required.every((column) => row[column].trim() !== '')
    ;(isComplete ? complete : incomplete).push(index)
  })
  return { complete, incomplete }
}

/** Splits the dataset in two, keeping each row's original position (rowIds). */
export function splitByCompleteness(dataset: Dataset, required: number[]): SplitResult {
  const { complete, incomplete } = splitRowIndexes(dataset.rows, required)
  const pick = (indexes: number[]): Dataset => ({
    ...dataset,
    rows: indexes.map((i) => dataset.rows[i]),
    rowIds: indexes.map((i) => dataset.rowIds[i]),
  })
  return { complete: pick(complete), incomplete: pick(incomplete) }
}
