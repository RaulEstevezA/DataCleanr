import { columnLabel, type Dataset } from '../core/dataset.ts'
import { useI18n } from '../i18n/useI18n.ts'
import './DatasetSummary.css'

interface DatasetSummaryProps {
  dataset: Dataset
  modifiedCells: number
  selectedColumn: number | null
  onSelectColumn: (index: number) => void
  onExport: () => void
  onReset: () => void
}

export function DatasetSummary({
  dataset,
  modifiedCells,
  selectedColumn,
  onSelectColumn,
  onExport,
  onReset,
}: DatasetSummaryProps) {
  const { t, language } = useI18n()
  const format = (n: number) => n.toLocaleString(language)

  return (
    <section className="panel dataset-summary">
      <div className="dataset-summary__header">
        <div>
          <h2 className="dataset-summary__file">{dataset.fileName}</h2>
          <p className="dataset-summary__stats">
            {t.rowCount(format(dataset.rows.length))} · {t.columnCount(format(dataset.columns.length))}
            {modifiedCells > 0 && (
              <span className="dataset-summary__modified"> · {t.modifiedCells(format(modifiedCells))}</span>
            )}
          </p>
        </div>
        <div className="dataset-summary__actions">
          <button type="button" className="button" onClick={onReset}>
            {t.importAnother}
          </button>
          <button type="button" className="button button--primary" onClick={onExport}>
            {t.exportCsv}
          </button>
        </div>
      </div>
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
