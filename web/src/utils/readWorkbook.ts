import type { XlsxSheet } from '../core/xlsx.ts'

/** Reads every sheet of an .xlsx file in the browser. The library is loaded only when needed. */
export async function readWorkbook(file: File): Promise<XlsxSheet[]> {
  const { default: readXlsxFile } = await import('read-excel-file/browser')
  // trim: false keeps spaces, which are part of what the user wants to see and clean
  return (await readXlsxFile(file, { trim: false })) as XlsxSheet[]
}
