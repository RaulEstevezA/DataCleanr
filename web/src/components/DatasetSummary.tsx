import { useRef } from 'react'
import { columnLabel, type Dataset } from '../core/dataset.ts'
import { useI18n } from '../i18n/useI18n.ts'
import './DatasetSummary.css'

interface DatasetSummaryProps {
  dataset: Dataset
  modifiedCells: number
  removedRows: number
  /** Sheet names when the file is an Excel workbook. */
  sheets: string[] | null
  onSelectSheet: (sheet: string) => void
  selectedColumn: number | null
  onSelectColumn: (index: number) => void
  onFindDuplicates: () => void
  onLoadProfile: (file: File) => void
  canUndo: boolean
  canRedo: boolean
  onUndo: () => void
  onRedo: () => void
  onExport: () => void
  onReset: () => void
}

const formatNames = { xlsx: 'Excel', json: 'JSON', xml: 'XML' }

export function DatasetSummary({
  dataset,
  modifiedCells,
  removedRows,
  sheets,
  onSelectSheet,
  selectedColumn,
  onSelectColumn,
  onFindDuplicates,
  onLoadProfile,
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  onExport,
  onReset,
}: DatasetSummaryProps) {
  const { t } = useI18n()
  const profileInput = useRef<HTMLInputElement>(null)

  return (
    <section className="panel dataset-summary">
      <div className="dataset-summary__header">
        <div>
          <h2 className="dataset-summary__file">{dataset.fileName}</h2>
          <p className="dataset-summary__stats">
            {t.rowCount(dataset.rows.length)} · {t.columnCount(dataset.columns.length)} ·{' '}
            {dataset.format === 'csv' ? dataset.encoding.toUpperCase() : formatNames[dataset.format]}
            {modifiedCells > 0 && (
              <span className="dataset-summary__modified"> · {t.modifiedCells(modifiedCells)}</span>
            )}
            {removedRows > 0 && <span className="dataset-summary__modified"> · {t.removedRows(removedRows)}</span>}
          </p>
        </div>
        <div className="dataset-summary__actions">
          <button type="button" className="button" disabled={!canUndo} onClick={onUndo} title={t.undoShortcut}>
            {t.undo}
          </button>
          <button type="button" className="button" disabled={!canRedo} onClick={onRedo} title={t.redoShortcut}>
            {t.redo}
          </button>
          <button type="button" className="button" onClick={onFindDuplicates}>
            {t.findDuplicates}
          </button>
          <button type="button" className="button" onClick={() => profileInput.current?.click()}>
            {t.loadProfile}
          </button>
          <input
            ref={profileInput}
            type="file"
            accept=".json,application/json"
            hidden
            onChange={(event) => {
              const file = event.target.files?.[0]
              if (file) onLoadProfile(file)
              event.target.value = ''
            }}
          />
          <button type="button" className="button" onClick={onReset}>
            {t.importAnother}
          </button>
          <button type="button" className="button button--primary" onClick={onExport}>
            {t.exportCsv}
          </button>
        </div>
      </div>
      {sheets && sheets.length > 1 && (
        <label className="dataset-summary__sheet">
          <span className="dataset-summary__label">{t.sheet}</span>
          <select value={dataset.sheet ?? ''} onChange={(event) => onSelectSheet(event.target.value)}>
            {sheets.map((sheet) => (
              <option key={sheet} value={sheet}>
                {sheet}
              </option>
            ))}
          </select>
        </label>
      )}
      <h3 className="dataset-summary__label">{t.detectedColumns}</h3>
      <ul className="dataset-summary__columns">
        {dataset.columns.map((_, i) => (
          <li key={i}>
            <button
              type="button"
              className="tag"
              aria-pressed={i === selectedColumn}
              onClick={() => onSelectColumn(i)}
            >
              {columnLabel(dataset, i)}
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
