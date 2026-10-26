import { describe, expect, it } from 'vitest'
import { cleanFileName, parseCsvText, serializeCsv } from './csv.ts'

describe('parseCsvText', () => {
  it('detects semicolon delimiters', () => {
    const dataset = parseCsvText('Empresa;Ciudad\nTransgrau;Valencia', 'a.csv')
    expect(dataset.delimiter).toBe(';')
    expect(dataset.rows).toEqual([['Transgrau', 'Valencia']])
  })

  it('keeps values and headers exactly as written', () => {
    const dataset = parseCsvText(' Empresa ,\n  TRANSGRAU ,x', 'a.csv')
    expect(dataset.columns).toEqual([' Empresa ', ''])
    expect(dataset.rows).toEqual([['  TRANSGRAU ', 'x']])
  })

  it('pads short rows and trims long ones', () => {
    const dataset = parseCsvText('a,b\n1\n1,2,3', 'a.csv')
    expect(dataset.rows).toEqual([
      ['1', ''],
      ['1', '2'],
    ])
  })

  it('ignores a UTF-8 byte order mark', () => {
    expect(parseCsvText('﻿Empresa\nx', 'a.csv').columns).toEqual(['Empresa'])
  })

  it('rejects empty files', () => {
    expect(() => parseCsvText('', 'a.csv')).toThrow()
  })
})

describe('serializeCsv', () => {
  it('starts with a UTF-8 byte order mark for Excel', () => {
    expect(serializeCsv(parseCsvText('a\n1', 'a.csv')).startsWith('﻿')).toBe(true)
  })

  it('reuses the original delimiter', () => {
    expect(serializeCsv(parseCsvText('a;b\n1;2', 'a.csv'))).toBe('﻿a;b\r\n1;2')
  })

  it('quotes values containing the delimiter, quotes or line breaks', () => {
    const csv = serializeCsv({ fileName: 'a.csv', delimiter: ',', encoding: 'utf-8', columns: ['a'], rows: [['x,y'], ['say "hi"'], ['l1\nl2']] })
    expect(csv).toBe('﻿a\r\n"x,y"\r\n"say ""hi"""\r\n"l1\nl2"')
  })

  it('round-trips through parseCsvText without changing any value', () => {
    const original = parseCsvText('Empresa;Nota\n  TRANSGRAU ;"a;b"\n;"dice ""hola"""', 'a.csv')
    expect(parseCsvText(serializeCsv(original), 'a.csv')).toEqual(original)
  })
})

describe('cleanFileName', () => {
  it('adds a _clean suffix', () => {
    expect(cleanFileName('clientes.csv')).toBe('clientes_clean.csv')
    expect(cleanFileName('Clientes.CSV')).toBe('Clientes_clean.csv')
    expect(cleanFileName('clientes')).toBe('clientes_clean.csv')
  })
})
