import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/similar.json'
import { comparisonKey, groupSimilarValues, similarity } from './similar.ts'

describe('comparisonKey', () => {
  it.each(cases.comparisonKey)('$description', ({ input, ignoreLegalForms, expected }) => {
    expect(comparisonKey(input, ignoreLegalForms)).toBe(expected)
  })
})

describe('similarity (same as RapidFuzz fuzz.ratio)', () => {
  it.each(cases.similarity)('"$a" vs "$b"', ({ a, b, expected }) => {
    expect(similarity(a, b)).toBeCloseTo(expected, 3)
  })
})

describe('groupSimilarValues', () => {
  it.each(cases.groups)('$description', ({ values, options, expected }) => {
    expect(groupSimilarValues(values, options)).toEqual(expected)
  })
})
