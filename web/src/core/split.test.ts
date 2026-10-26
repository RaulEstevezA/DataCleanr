import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/split.json'
import { splitByCompleteness, splitRowIndexes } from './split.ts'

it.each(cases)('$description', ({ rows, required, expected }) => {
  expect(splitRowIndexes(rows, required)).toEqual(expected)
})

it('keeps the original row numbers in each part', () => {
  const dataset = {
    fileName: 'a.csv',
    format: 'csv' as const,
    sheet: null,
    columns: ['a', 'b'],
    rows: [['1', ''], ['2', 'x']],
    rowIds: [4, 7],
    delimiter: ',',
    encoding: 'utf-8' as const,
  }
  const { complete, incomplete } = splitByCompleteness(dataset, [0, 1])
  expect(complete.rowIds).toEqual([7])
  expect(incomplete.rowIds).toEqual([4])
})
