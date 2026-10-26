import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/duplicates.json'
import { findDuplicateRows } from './duplicates.ts'

it.each(cases)('$description', ({ rows, options, expected }) => {
  expect(findDuplicateRows(rows, options)).toEqual(expected)
})
