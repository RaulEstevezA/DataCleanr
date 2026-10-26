import { describe, expect, it } from 'vitest'
import { applyColumnChanges, previewColumnChanges } from './changes.ts'
import type { Dataset } from './dataset.ts'
import { transforms } from './transforms.ts'

const dataset: Dataset = {
  fileName: 'test.csv',
  delimiter: ',',
  encoding: 'utf-8',
  columns: ['Empresa', 'Ciudad'],
  rows: [
    ['  TRANSGRAU ', ' Valencia'],
    ['Trans Grau SL', 'Bilbao'],
    ['', 'madrid '],
  ],
}

describe('previewColumnChanges', () => {
  it('returns only the cells that would change', () => {
    expect(previewColumnChanges(dataset, 1, transforms.trim)).toEqual([
      { row: 0, original: ' Valencia', proposed: 'Valencia' },
      { row: 2, original: 'madrid ', proposed: 'madrid' },
    ])
  })

  it('returns no changes when the column is already clean', () => {
    expect(previewColumnChanges(dataset, 0, (value) => value)).toEqual([])
  })
})

describe('applyColumnChanges', () => {
  it('applies the given changes to the column', () => {
    const changes = previewColumnChanges(dataset, 1, transforms.trim)
    const result = applyColumnChanges(dataset, 1, changes)
    expect(result.rows.map((row) => row[1])).toEqual(['Valencia', 'Bilbao', 'madrid'])
  })

  it('only applies the accepted subset', () => {
    const [first] = previewColumnChanges(dataset, 1, transforms.trim)
    const result = applyColumnChanges(dataset, 1, [first])
    expect(result.rows.map((row) => row[1])).toEqual(['Valencia', 'Bilbao', 'madrid '])
  })

  it('does not mutate the original dataset', () => {
    const snapshot = structuredClone(dataset)
    applyColumnChanges(dataset, 0, previewColumnChanges(dataset, 0, transforms.trim))
    expect(dataset).toEqual(snapshot)
  })

  it('leaves other columns untouched', () => {
    const result = applyColumnChanges(dataset, 0, previewColumnChanges(dataset, 0, transforms.trim))
    expect(result.rows.map((row) => row[1])).toEqual([' Valencia', 'Bilbao', 'madrid '])
  })
})
