import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/duplicates.json'
import similarCases from '../../../shared/test-cases/similar-rows.json'
import { findDuplicateRows, findSimilarRows } from './duplicates.ts'

describe('findDuplicateRows', () => {
  it.each(cases)('$description', ({ rows, options, expected }) => {
    expect(findDuplicateRows(rows, options)).toEqual(expected)
  })
})

describe('findSimilarRows', () => {
  it.each(similarCases)('$description', ({ rows, options, expected }) => {
    const groups = findSimilarRows(rows, options)
    expect(groups.map((group) => group.rows)).toEqual(expected.map((group) => group.rows))
    groups.forEach((group, g) => {
      group.scores.forEach((score, i) => expect(score).toBeCloseTo(expected[g].scores[i], 3))
    })
  })
})
