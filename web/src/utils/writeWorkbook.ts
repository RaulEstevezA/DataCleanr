import type { Dataset } from '../core/dataset.ts'
import type { ColumnType } from '../core/export.ts'
import { datasetToSheetData } from '../core/xlsxSheet.ts'

/** Builds an .xlsx file in memory. The library is loaded only when needed. */
export async function writeWorkbook(dataset: Dataset, types: ColumnType[]): Promise<Blob> {
  const { default: writeXlsxFile } = await import('write-excel-file/browser')
  const data = datasetToSheetData(dataset, types)
  // Freeze the header row so it stays visible while scrolling in Excel
  return writeXlsxFile(data as never, { sheet: dataset.sheet ?? 'Data', stickyRowsCount: 1 }).toBlob()
}
