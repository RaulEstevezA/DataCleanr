import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import readXlsxFile from 'read-excel-file/node'
import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/xlsx.json'
import { EmptySheetError, sheetToDataset, type XlsxSheet } from './xlsx.ts'

describe.each(cases.files)('xlsx import: $file', async ({ file, sheets: expectedSheets }) => {
  const filePath = fileURLToPath(new URL(`../../../shared/test-cases/${file}`, import.meta.url))
  const sheets = (await readXlsxFile(readFileSync(filePath), { trim: false })) as XlsxSheet[]

  it('reads every sheet in order', () => {
    expect(sheets.map(({ sheet }) => sheet)).toEqual(expectedSheets.map(({ sheet }) => sheet))
  })

  it.each(expectedSheets)('sheet "$sheet"', (expected) => {
    const sheet = sheets.find(({ sheet }) => sheet === expected.sheet)!
    if ('empty' in expected) {
      expect(() => sheetToDataset(sheet, file)).toThrow(EmptySheetError)
      return
    }
    const dataset = sheetToDataset(sheet, file)
    expect(dataset.columns).toEqual(expected.columns)
    expect(dataset.rows).toEqual(expected.rows)
    expect(dataset.sheet).toBe(expected.sheet)
  })
})
