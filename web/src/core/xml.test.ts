// @vitest-environment jsdom
import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/xml.json'
import { parseXmlText, XmlImportError } from './xml.ts'

function reasonOf(run: () => unknown): string | null {
  try {
    run()
    return null
  } catch (error) {
    return error instanceof XmlImportError ? error.reason : 'unexpected error'
  }
}

it.each(cases)('$description', ({ input, expected }) => {
  if ('error' in expected) {
    expect(reasonOf(() => parseXmlText(input, 'a.xml'))).toBe(expected.error)
    return
  }
  const dataset = parseXmlText(input, 'a.xml')
  expect(dataset.columns).toEqual(expected.columns)
  expect(dataset.rows).toEqual(expected.rows)
})
