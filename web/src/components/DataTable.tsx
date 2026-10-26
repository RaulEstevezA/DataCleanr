import { useState } from 'react'
import { columnLabel, type Dataset } from '../core/dataset.ts'
import { useI18n } from '../i18n/useI18n.ts'
import './DataTable.css'

const PAGE_SIZE = 50

interface DataTableProps {
  dataset: Dataset
  selectedColumn: number | null
  onSelectColumn: (index: number) => void
}

export function DataTable({ dataset, selectedColumn, onSelectColumn }: DataTableProps) {
  const { t } = useI18n()
  const [page, setPage] = useState(0)

  const totalRows = dataset.rows.length
  const pageCount = Math.max(1, Math.ceil(totalRows / PAGE_SIZE))
  const start = page * PAGE_SIZE
  const visibleRows = dataset.rows.slice(start, start + PAGE_SIZE)

  return (
    <section className="panel data-table">
      <div className="data-table__scroll">
        <table>
          <thead>
            <tr>
              <th className="data-table__index">#</th>
              {dataset.columns.map((_, i) => (
                <th key={i} aria-selected={i === selectedColumn}>
                  <button type="button" onClick={() => onSelectColumn(i)}>
                    {columnLabel(dataset, i)}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, r) => (
              <tr key={start + r}>
                <td className="data-table__index">{start + r + 1}</td>
                {row.map((cell, c) => (
                  <td key={c} aria-selected={c === selectedColumn}>
                    {cell === '' ? <span className="data-table__empty">{t.emptyCell}</span> : cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {pageCount > 1 && (
        <nav className="data-table__pagination" aria-label={t.pagination}>
          <button type="button" className="button" disabled={page === 0} onClick={() => setPage(page - 1)}>
            {t.previous}
          </button>
          <span>
            {t.rowRange(start + 1, start + visibleRows.length, totalRows)}
          </span>
          <button
            type="button"
            className="button"
            disabled={page >= pageCount - 1}
            onClick={() => setPage(page + 1)}
          >
            {t.next}
          </button>
        </nav>
      )}
    </section>
  )
}
