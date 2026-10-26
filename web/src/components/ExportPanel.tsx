import { useMemo, useState } from 'react'
import { cleanFileName, serializeCsv } from '../core/csv.ts'
import { columnLabel, type Dataset } from '../core/dataset.ts'
import { countTextFallbacks, suggestColumnType, type ColumnType } from '../core/export.ts'
import { splitByCompleteness } from '../core/split.ts'
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
  const [format, setFormat] = useState<Format>(dataset.format === 'xlsx' ? 'xlsx' : 'csv')
  const [delimiter, setDelimiter] = useState(DELIMITERS.includes(dataset.delimiter) ? dataset.delimiter : ',')
  const columnValues = useMemo(
    () => dataset.columns.map((_, c) => dataset.rows.map((row) => row[c])),
    [dataset],
  )
  const suggested = useMemo(() => columnValues.map(suggestColumnType), [columnValues])
  const [types, setTypes] = useState<ColumnType[]>(suggested)
  const [exporting, setExporting] = useState(false)
  const [failed, setFailed] = useState(false)
  // Optional split: complete rows (a value in every required column) and incomplete ones
  const [split, setSplit] = useState(false)
  const [required, setRequired] = useState<Set<number>>(() => new Set(dataset.columns.map((_, i) => i)))
  const parts = useMemo(
    () => splitByCompleteness(dataset, [...required].sort((a, b) => a - b)),
    [dataset, required],
  )
  // Empty parts are not exported
  const exportedParts = split
    ? [
        { part: 'complete', sheet: t.sheetComplete, dataset: parts.complete },
        { part: 'incomplete', sheet: t.sheetIncomplete, dataset: parts.incomplete },
      ].filter(({ dataset: d }) => d.rows.length > 0)
    : [{ part: undefined, sheet: dataset.sheet ?? 'Data', dataset }]
  const fileNames =
    format === 'xlsx' || !split
      ? [cleanFileName(dataset.fileName, format)]
      : exportedParts.map(({ part }) => cleanFileName(dataset.fileName, 'csv', part))

  function toggleRequired(column: number) {
    const next = new Set(required)
    if (next.has(column)) next.delete(column)
    else next.add(column)
    setRequired(next)
  }

  async function download() {
    setExporting(true)
    setFailed(false)
    try {
      if (format === 'csv') {
        for (const { part, dataset: d } of exportedParts) {
          const csv = serializeCsv({ ...d, delimiter })
          downloadBlob(new Blob([csv], { type: 'text/csv;charset=utf-8' }), cleanFileName(d.fileName, 'csv', part))
        }
      } else {
        const sheets = exportedParts.map(({ sheet, dataset: d }) => ({ name: sheet, dataset: d }))
        downloadBlob(await writeWorkbook(sheets, types), cleanFileName(dataset.fileName, 'xlsx'))
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

      <div className="export__split">
        <label className="transform-panel__check">
          <input type="checkbox" checked={split} onChange={(event) => setSplit(event.target.checked)} />
          {t.exportSplit}
        </label>
        {split && (
          <>
            <span className="duplicates__label">{t.exportRequired}</span>
            <div className="duplicates__columns">
              {dataset.columns.map((_, c) => (
                <button
                  key={c}
                  type="button"
                  className="tag"
                  aria-pressed={required.has(c)}
                  onClick={() => toggleRequired(c)}
                >
                  {columnLabel(dataset, c)}
                </button>
              ))}
            </div>
            <p className="transform-panel__info">
              {t.splitCounts(parts.complete.rows.length, parts.incomplete.rows.length)}
            </p>
            {exportedParts.length < 2 && <p className="transform-panel__hint">{t.splitSinglePart}</p>}
            <p className="transform-panel__hint">{format === 'csv' ? t.exportSplitCsvHint : t.exportSplitXlsxHint}</p>
          </>
        )}
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
        <span className="transform-panel__info">{fileNames.join(' · ')}</span>
        <button type="button" className="button button--primary" disabled={exporting} onClick={download}>
          {exporting ? t.exporting : t.download}
        </button>
      </div>
    </section>
  )
}
