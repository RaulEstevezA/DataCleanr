import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/xlsx-export.json'
import { suggestColumnType, toTypedCell, type ColumnType } from './export.ts'

describe('toTypedCell', () => {
  it.each(cases.conversions)('$description', ({ value, type, expected }) => {
    expect(toTypedCell(value, type as ColumnType)).toEqual(expected)
  })
})

describe('suggestColumnType', () => {
  it.each(cases.suggestions)('$description', ({ values, expected }) => {
    expect(suggestColumnType(values)).toBe(expected)
  })
})
