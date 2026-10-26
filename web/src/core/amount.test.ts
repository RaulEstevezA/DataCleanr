import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/amount.json'
import { normalizeAmount, type AmountOptions } from './amount.ts'

it.each(cases)('$description', ({ options, input, expected, expectedStatus, ...rest }) => {
  const result = normalizeAmount(input, options as AmountOptions)
  expect({ status: result.status, value: result.value }).toEqual({ status: expectedStatus, value: expected })
  if ('expectedCurrency' in rest) expect(result.currency).toBe(rest.expectedCurrency)
})
