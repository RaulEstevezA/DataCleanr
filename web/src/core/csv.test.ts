import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/csv.json'
import { cleanFileName, CsvParseError, parseCsvText, serializeCsv } from './csv.ts'

describe('parseCsvText (shared cases)', () => {
  it.each(cases.import)('$description', ({ input, expected }) => {
    if ('error' in expected) {
      expect(() => parseCsvText(input, 'a.csv')).toThrow(CsvParseError)
      return
    }
    const { delimiter, columns, rows } = parseCsvText(input, 'a.csv')
    expect({ delimiter, columns, rows }).toEqual(expected)
  })
})

describe('serializeCsv (shared cases)', () => {
  it.each(cases.export)('$description', ({ columns, rows, delimiter, expected }) => {
    const dataset = {
      fileName: 'a.csv',
      format: 'csv' as const,
      sheet: null,
      columns,
      rows,
      rowIds: rows.map((_, i) => i),
      delimiter,
      encoding: 'utf-8' as const,
    }
    expect(serializeCsv(dataset)).toBe(expected)
  })
})

it('round-trips through parseCsvText without changing any value', () => {
  const original = parseCsvText('Empresa;Nota\n  TRANSGRAU ;"a;b"\n;"dice ""hola"""', 'a.csv')
  expect(parseCsvText(serializeCsv(original), 'a.csv')).toEqual(original)
})

describe('cleanFileName', () => {
  it('adds a _clean suffix', () => {
    expect(cleanFileName('clientes.csv')).toBe('clientes_clean.csv')
    expect(cleanFileName('Clientes.CSV')).toBe('Clientes_clean.csv')
    expect(cleanFileName('clientes')).toBe('clientes_clean.csv')
    expect(cleanFileName('clientes.xlsx')).toBe('clientes_clean.csv')
    expect(cleanFileName('clientes.csv', 'xlsx')).toBe('clientes_clean.xlsx')
    expect(cleanFileName('clientes.json')).toBe('clientes_clean.csv')
    expect(cleanFileName('clientes.xml')).toBe('clientes_clean.csv')
  })
})
