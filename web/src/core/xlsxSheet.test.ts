import readXlsxFile from 'read-excel-file/node'
import writeXlsxFile from 'write-excel-file/node'
import { expect, it } from 'vitest'
import type { Dataset } from './dataset.ts'
import { datasetToSheetData } from './xlsxSheet.ts'
import { sheetToDataset, type XlsxSheet } from './xlsx.ts'

const dataset: Dataset = {
  fileName: 'a.csv',
  format: 'csv',
  sheet: null,
  columns: ['ID', 'Fecha', 'Importe', 'Activo', 'Código'],
  rows: [
    ['1001', '2024-07-13', '5837.32', 'TRUE', '007'],
    ['1002', '2024-01-12 10:30:00', '-0.1', 'false', '46001'],
    ['', '13/07/2024', '1234,56', '', ''],
  ],
  rowIds: [0, 1, 2],
  delimiter: ',',
  encoding: 'utf-8',
}

it('round-trips through a real .xlsx file without shifting dates or changing values', async () => {
  const data = datasetToSheetData(dataset, ['number', 'date', 'number', 'boolean', 'text'])
  // write-excel-file types are stricter than needed for plain cells
  const buffer = await writeXlsxFile(data as never, { sheet: 'Datos' }).toBuffer()
  const sheets = (await readXlsxFile(buffer, { trim: false })) as XlsxSheet[]
  const back = sheetToDataset(sheets[0], 'a.xlsx')

  expect(back.sheet).toBe('Datos')
  expect(back.columns).toEqual(dataset.columns)
  expect(back.rows).toEqual([
    ['1001', '2024-07-13', '5837.32', 'TRUE', '007'],
    ['1002', '2024-01-12 10:30:00', '-0.1', 'FALSE', '46001'],
    // Values that cannot be converted stay as text, untouched
    ['', '13/07/2024', '1234,56', '', ''],
  ])
})
