import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import readXlsxFile from 'read-excel-file/node'
import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/xlsx.json'
import { EmptySheetError, sheetToDataset, type XlsxSheet } from './xlsx.ts'

const filePath = fileURLToPath(new URL(`../../../shared/test-cases/${cases.file}`, import.meta.url))

describe('xlsx import (shared sample file)', async () => {
  const sheets = (await readXlsxFile(readFileSync(filePath), { trim: false })) as XlsxSheet[]

  it('reads every sheet in order', () => {
    expect(sheets.map(({ sheet }) => sheet)).toEqual(cases.sheets.map(({ sheet }) => sheet))
  })

  it.each(cases.sheets)('sheet "$sheet"', (expected) => {
    const sheet = sheets.find(({ sheet }) => sheet === expected.sheet)!
    if ('empty' in expected) {
      expect(() => sheetToDataset(sheet, 'sample.xlsx')).toThrow(EmptySheetError)
      return
    }
    const dataset = sheetToDataset(sheet, 'sample.xlsx')
    expect(dataset.columns).toEqual(expected.columns)
    expect(dataset.rows).toEqual(expected.rows)
    expect(dataset.sheet).toBe(expected.sheet)
  })
})
