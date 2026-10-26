import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/transforms.json'
import { transformIds, transforms } from './transforms.ts'

describe.each(transformIds)('%s', (id) => {
  it.each(cases[id])('$description', ({ input, expected }) => {
    expect(transforms[id](input)).toBe(expected)
  })
})

it('every transform has shared test cases', () => {
  expect(Object.keys(cases).sort()).toEqual([...transformIds].sort())
})
