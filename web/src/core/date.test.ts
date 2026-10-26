import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/date.json'
import { normalizeDate, type DateOptions } from './date.ts'

it.each(cases)('$description', ({ options, input, expected, expectedStatus }) => {
  expect(normalizeDate(input, options as DateOptions)).toEqual({ status: expectedStatus, value: expected })
})
