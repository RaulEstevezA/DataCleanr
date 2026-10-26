import { describe, expect, it } from 'vitest'
import { messages } from './messages.ts'

describe('count messages', () => {
  it('use singular for one', () => {
    expect(messages.es.columnCount(1)).toBe('1 columna')
    expect(messages.en.columnCount(1)).toBe('1 column')
    expect(messages.es.applyChanges(1)).toBe('Aplicar 1 cambio')
    expect(messages.es.changesSelected(1, 1)).toBe('1 de 1 cambio seleccionado')
  })

  it('use plural for zero and many', () => {
    expect(messages.es.columnCount(0)).toBe('0 columnas')
    expect(messages.es.rowCount(126)).toBe('126 filas')
    expect(messages.en.applyChanges(2)).toBe('Apply 2 changes')
    expect(messages.es.changesSelected(1, 5)).toBe('1 de 5 cambios seleccionados')
  })

  it('format numbers with each language separators', () => {
    expect(messages.es.rowCount(12345)).toBe('12.345 filas')
    expect(messages.en.rowCount(12345)).toBe('12,345 rows')
  })
})
