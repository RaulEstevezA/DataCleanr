import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/replace.json'
import { createReplaceTransform } from './replace.ts'

it.each(cases)('$description', ({ options, input, expected }) => {
  expect(createReplaceTransform(options)(input)).toBe(expected)
})
