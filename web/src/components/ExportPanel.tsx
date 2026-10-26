import { useMemo, useState } from 'react'
import { cleanFileName, serializeCsv } from '../core/csv.ts'
import { columnLabel, type Dataset } from '../core/dataset.ts'
import { countTextFallbacks, suggestColumnType, type ColumnType } from '../core/export.ts'
import { useI18n } from '../i18n/useI18n.ts'
import { downloadBlob } from '../utils/download.ts'
import { writeWorkbook } from '../utils/writeWorkbook.ts'
import './ExportPanel.css'

type Format = 'csv' | 'xlsx'

const DELIMITERS = [';', ',', '\t']
const COLUMN_TYPES: ColumnType[] = ['text', 'number', 'date', 'boolean']

interface ExportPanelProps {
  dataset: Dataset
  onClose: () => void
}

export function ExportPanel({ dataset, onClose }: ExportPanelProps) {
  const { t } = useI18n()
  const [format, setFormat] = useState<Format>(dataset.format)
  const [delimiter, setDelimiter] = useState(DELIMITERS.includes(dataset.delimiter) ? dataset.delimiter : ',')
  const columnValues = useMemo(
    () => dataset.columns.map((_, c) => dataset.rows.map((row) => row[c])),
    [dataset],
  )
  const suggested = useMemo(() => columnValues.map(suggestColumnType), [columnValues])
  const [types, setTypes] = useState<ColumnType[]>(suggested)
  const [exporting, setExporting] = useState(false)
  const [failed, setFailed] = useState(false)

  async function download() {
    setExporting(true)
    setFailed(false)
    try {
      if (format === 'csv') {
        const csv = serializeCsv({ ...dataset, delimiter })
        downloadBlob(new Blob([csv], { type: 'text/csv;charset=utf-8' }), cleanFileName(dataset.fileName, 'csv'))
      } else {
        downloadBlob(await writeWorkbook(dataset, types), cleanFileName(dataset.fileName, 'xlsx'))
      }
    } catch {
      setFailed(true)
    } finally {
      setExporting(false)
    }
  }

  return (
    <section className="panel export">
      <div className="duplicates__header">
        <h2 className="transform-panel__title">{t.exportTitle}</h2>
        <button type="button" className="button" onClick={onClose}>
          {t.close}
        </button>
      </div>

      <div className="duplicates__modes" role="group" aria-label={t.exportFormat}>
        <button type="button" className="button" aria-pressed={format === 'csv'} onClick={() => setFormat('csv')}>
          CSV
        </button>
        <button type="button" className="button" aria-pressed={format === 'xlsx'} onClick={() => setFormat('xlsx')}>
          Excel (.xlsx)
        </button>
      </div>

      {format === 'csv' ? (
        <div className="export__csv">
          <label className="export__field">
            <span>{t.exportDelimiter}</span>
            <select value={delimiter} onChange={(event) => setDelimiter(event.target.value)}>
              {DELIMITERS.map((d) => (
                <option key={d} value={d}>
                  {t.delimiterNames[d as keyof typeof t.delimiterNames]}
                </option>
              ))}
            </select>
          </label>
          <p className="transform-panel__hint">{t.exportCsvHint}</p>
        </div>
      ) : (
        <>
          <p className="transform-panel__hint">{t.exportTypesHint}</p>
          <div className="export__scroll">
            <table className="export__types">
              <thead>
                <tr>
                  <th>{t.exportColumn}</th>
                  <th>{t.exportType}</th>
                  <th>{t.exportExample}</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {dataset.columns.map((_, c) => {
                  const fallbacks = countTextFallbacks(columnValues[c], types[c])
                  const example = columnValues[c].find((value) => value !== '') ?? ''
                  return (
                    <tr key={c}>
                      <td>{columnLabel(dataset, c)}</td>
                      <td>
                        <select
                          aria-label={t.exportTypeOf(columnLabel(dataset, c))}
                          value={types[c]}
                          onChange={(event) =>
                            setTypes(types.map((type, i) => (i === c ? (event.target.value as ColumnType) : type)))
                          }
                        >
                          {COLUMN_TYPES.map((type) => (
                            <option key={type} value={type}>
                              {t.columnTypeNames[type]}
                              {type === suggested[c] ? ` (${t.exportSuggested})` : ''}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="export__example">{example}</td>
                      <td className="export__warning">{fallbacks > 0 && t.exportFallbacks(fallbacks)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {failed && (
        <p className="transform-panel__warning" role="alert">
          {t.exportError}
        </p>
      )}
      <div className="transform-panel__actions">
        <span className="transform-panel__info">{cleanFileName(dataset.fileName, format)}</span>
        <button type="button" className="button button--primary" disabled={exporting} onClick={download}>
          {exporting ? t.exporting : t.download}
        </button>
      </div>
    </section>
  )
}
