import { useMemo, useState } from 'react'
import { columnLabel, removeRows, rowNumber, type Dataset } from '../core/dataset.ts'
import { findDuplicateRows } from '../core/duplicates.ts'
import { useI18n } from '../i18n/useI18n.ts'
import { VisibleText } from './VisibleText.tsx'
import './DuplicatesPanel.css'

// Rendering thousands of groups at once would freeze the page
const MAX_VISIBLE_GROUPS = 100

interface DuplicatesPanelProps {
  dataset: Dataset
  onRemove: (dataset: Dataset, removedCount: number) => void
  onClose: () => void
}

export function DuplicatesPanel({ dataset, onRemove, onClose }: DuplicatesPanelProps) {
  const { t } = useI18n()
  const [columns, setColumns] = useState<Set<number>>(() => new Set(dataset.columns.map((_, i) => i)))
  const [ignoreCaseAndSpaces, setIgnoreCaseAndSpaces] = useState(false)
  // Per group: which row to keep (default: the first one) and whether the group is excluded
  const [kept, setKept] = useState<Record<number, number>>({})
  const [excluded, setExcluded] = useState<Set<number>>(new Set())

  const groups = useMemo(
    () => findDuplicateRows(dataset.rows, { columns: [...columns].sort((a, b) => a - b), ignoreCaseAndSpaces }),
    [dataset, columns, ignoreCaseAndSpaces],
  )
  const toRemove = useMemo(() => {
    const indexes = new Set<number>()
    groups.forEach((group, g) => {
      if (excluded.has(g)) return
      const keep = kept[g] ?? group[0]
      for (const row of group) if (row !== keep) indexes.add(row)
    })
    return indexes
  }, [groups, kept, excluded])

  function resetChoices() {
    setKept({})
    setExcluded(new Set())
  }

  function toggleColumn(column: number) {
    const next = new Set(columns)
    if (next.has(column)) next.delete(column)
    else next.add(column)
    setColumns(next)
    resetChoices()
  }

  function toggleGroup(group: number) {
    const next = new Set(excluded)
    if (next.has(group)) next.delete(group)
    else next.add(group)
    setExcluded(next)
  }

  return (
    <section className="panel duplicates">
      <div className="duplicates__header">
        <h2 className="transform-panel__title">{t.duplicatesTitle}</h2>
        <button type="button" className="button" onClick={onClose}>
          {t.close}
        </button>
      </div>

      <div className="duplicates__options">
        <span className="duplicates__label">{t.duplicatesCompare}</span>
        <div className="duplicates__columns">
          {dataset.columns.map((_, i) => (
            <button key={i} type="button" className="tag" aria-pressed={columns.has(i)} onClick={() => toggleColumn(i)}>
              {columnLabel(dataset, i)}
            </button>
          ))}
        </div>
        <label className="transform-panel__check">
          <input
            type="checkbox"
            checked={ignoreCaseAndSpaces}
            onChange={(event) => {
              setIgnoreCaseAndSpaces(event.target.checked)
              resetChoices()
            }}
          />
          {t.duplicatesIgnoreCase}
        </label>
        <p className="transform-panel__hint">{t.duplicatesHint}</p>
      </div>

      {columns.size === 0 && <p className="transform-panel__info">{t.duplicatesNoColumns}</p>}
      {columns.size > 0 && groups.length === 0 && <p className="transform-panel__info">{t.duplicatesNone}</p>}

      {groups.length > 0 && (
        <>
          <ul className="duplicates__groups">
            {groups.slice(0, MAX_VISIBLE_GROUPS).map((group, g) => {
              const keep = kept[g] ?? group[0]
              const isExcluded = excluded.has(g)
              return (
                <li key={group[0]} className={`duplicates__group${isExcluded ? ' duplicates__group--excluded' : ''}`}>
                  <label className="transform-panel__check duplicates__group-title">
                    <input type="checkbox" checked={!isExcluded} onChange={() => toggleGroup(g)} />
                    {t.duplicatesGroup(group.length)}
                  </label>
                  <div className="duplicates__scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>{t.duplicatesKeep}</th>
                          <th>#</th>
                          {dataset.columns.map((_, c) => (
                            <th key={c} aria-selected={columns.has(c)}>
                              {columnLabel(dataset, c)}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {group.map((row) => (
                          <tr key={row} className={!isExcluded && row !== keep ? 'duplicates__removed' : undefined}>
                            <td>
                              <input
                                type="radio"
                                name={`keep-${group[0]}`}
                                aria-label={t.duplicatesKeepRow(rowNumber(dataset, row))}
                                checked={row === keep}
                                disabled={isExcluded}
                                onChange={() => setKept({ ...kept, [g]: row })}
                              />
                            </td>
                            <td className="transform-panel__index">{rowNumber(dataset, row)}</td>
                            {dataset.rows[row].map((cell, c) => (
                              <td key={c} aria-selected={columns.has(c)}>
                                <VisibleText value={cell} />
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </li>
              )
            })}
          </ul>
          {groups.length > MAX_VISIBLE_GROUPS && (
            <p className="transform-panel__info">{t.duplicatesTruncated(MAX_VISIBLE_GROUPS, groups.length)}</p>
          )}
          <div className="transform-panel__actions">
            <span className="transform-panel__info">{t.duplicatesSummary(groups.length, toRemove.size)}</span>
            <button
              type="button"
              className="button button--primary"
              disabled={toRemove.size === 0}
              onClick={() => onRemove(removeRows(dataset, toRemove), toRemove.size)}
            >
              {t.duplicatesRemove(toRemove.size)}
            </button>
          </div>
        </>
      )}
    </section>
  )
}
