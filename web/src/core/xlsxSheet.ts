import type { Dataset } from './dataset.ts'
import { toTypedCell, type ColumnType } from './export.ts'

/** Cell in the shape expected by write-excel-file (kept here so it can be tested without the library). */
export interface SheetCell {
  type?: StringConstructor | NumberConstructor | DateConstructor | BooleanConstructor
  value?: string | number | Date | boolean
  format?: string
  fontWeight?: 'bold'
}

function toSheetCell(value: string, type: ColumnType): SheetCell | null {
  const cell = toTypedCell(value, type)
  switch (cell.type) {
    case 'empty':
      return null
    case 'number':
      return { type: Number, value: cell.value }
    case 'boolean':
      return { type: Boolean, value: cell.value }
    case 'date': {
      const [date, time = '00:00:00'] = cell.value.split(' ')
      const [year, month, day] = date.split('-').map(Number)
      const [hours, minutes, seconds] = time.split(':').map(Number)
      // UTC on purpose: Excel dates have no time zone, so no shift depending on where the user is
      return {
        type: Date,
        value: new Date(Date.UTC(year, month - 1, day, hours, minutes, seconds)),
        format: cell.value.includes(' ') ? 'yyyy-mm-dd hh:mm:ss' : 'yyyy-mm-dd',
      }
    }
    case 'text':
      return { type: String, value: cell.value }
  }
}

/** Header (bold) plus every row, each cell converted to its column's type. */
export function datasetToSheetData(dataset: Dataset, types: ColumnType[]): (SheetCell | null)[][] {
  const header = dataset.columns.map((name) => ({ type: String, value: name, fontWeight: 'bold' as const }))
  return [header, ...dataset.rows.map((row) => row.map((value, c) => toSheetCell(value, types[c])))]
}
