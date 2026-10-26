import type { Dataset } from '../core/dataset.ts'
import type { ColumnType } from '../core/export.ts'
import { datasetToSheetData } from '../core/xlsxSheet.ts'

export interface WorkbookSheet {
  name: string
  dataset: Dataset
}

/** Builds an .xlsx file in memory, one sheet per entry. The library is loaded only when needed. */
export async function writeWorkbook(sheets: WorkbookSheet[], types: ColumnType[]): Promise<Blob> {
  const { default: writeXlsxFile } = await import('write-excel-file/browser')
  // Freeze the header row so it stays visible while scrolling in Excel
  const content = sheets.map(({ name, dataset }) => ({
    data: datasetToSheetData(dataset, types),
    sheet: name,
    stickyRowsCount: 1,
  }))
  return writeXlsxFile(content as never).toBlob()
}
