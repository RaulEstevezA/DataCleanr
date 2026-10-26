import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/json.json'
import { JsonImportError, parseJsonText } from './json.ts'

function reasonOf(run: () => unknown): string | null {
  try {
    run()
    return null
  } catch (error) {
    return error instanceof JsonImportError ? error.reason : 'unexpected error'
  }
}

it.each(cases)('$description', ({ input, expected }) => {
  if ('error' in expected) {
    expect(reasonOf(() => parseJsonText(input, 'a.json'))).toBe(expected.error)
    return
  }
  const dataset = parseJsonText(input, 'a.json')
  expect(dataset.columns).toEqual(expected.columns)
  expect(dataset.rows).toEqual(expected.rows)
})
