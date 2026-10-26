import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/phone.json'
import { normalizePhone, type PhoneOptions } from './phone.ts'

it.each(cases)('$description', ({ options, input, expected, expectedStatus }) => {
  expect(normalizePhone(input, options as PhoneOptions)).toEqual({ status: expectedStatus, value: expected })
})
