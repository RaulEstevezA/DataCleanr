import type { Dataset } from '../lib/dataset.ts'
import { useI18n } from '../i18n/useI18n.ts'
import './DatasetSummary.css'

interface DatasetSummaryProps {
  dataset: Dataset
  onReset: () => void
}

export function DatasetSummary({ dataset, onReset }: DatasetSummaryProps) {
  const { t, language } = useI18n()
  const format = (n: number) => n.toLocaleString(language)

  return (
    <section className="panel dataset-summary">
      <div className="dataset-summary__header">
        <div>
          <h2 className="dataset-summary__file">{dataset.fileName}</h2>
          <p className="dataset-summary__stats">
            {t.rowCount(format(dataset.rows.length))} · {t.columnCount(format(dataset.columns.length))}
          </p>
        </div>
        <button type="button" className="button" onClick={onReset}>
          {t.importAnother}
        </button>
      </div>
      <h3 className="dataset-summary__label">{t.detectedColumns}</h3>
      <ul className="dataset-summary__columns">
        {dataset.columns.map((column, i) => (
          <li key={i} className="tag">
            {column}
          </li>
        ))}
      </ul>
    </section>
  )
}
