import { useMemo, useState } from 'react'
import { columnLabel, removeRows, rowNumber, type Dataset } from '../core/dataset.ts'
import {
  findDuplicateRows,
  findSimilarRows,
  mergeRows,
  type MergedRow,
  type SimilarRowsOptions,
} from '../core/duplicates.ts'
import type { ProfileStep } from '../core/profile.ts'
import { useStoredState } from '../hooks/useStoredState.ts'
import { useI18n } from '../i18n/useI18n.ts'
import { VisibleText } from './VisibleText.tsx'
import './DuplicatesPanel.css'
import './SimilarValuesForm.css'

// Rendering thousands of groups at once would freeze the page
const MAX_VISIBLE_GROUPS = 100
// Possible duplicates compare rows pairwise: beyond this the page could freeze for several seconds
const MAX_ROWS_FOR_SIMILAR = 5000

type Mode = 'exact' | 'similar'

type SimilarSettings = Omit<SimilarRowsOptions, 'columns'>

const defaultSimilarSettings = (): SimilarSettings => ({ threshold: 85, ignoreLegalForms: true })

interface Group {
  rows: number[]
  /** Similarity to the group's first row; only for possible duplicates. */
  scores?: number[]
}

/** What will happen to one included group. */
interface GroupPlan {
  keep: number
  remove: number[]
  /** Kept row after filling its empty cells; null when merging is off. */
  merged: MergedRow | null
}

interface DuplicatesPanelProps {
  dataset: Dataset
  /** `step` is null when the operation cannot be replayed in a profile (possible duplicates). */
  onRemove: (dataset: Dataset, removedCount: number, mode: Mode, filledCount: number, step: ProfileStep | null) => void
  onClose: () => void
}

export function DuplicatesPanel({ dataset, onRemove, onClose }: DuplicatesPanelProps) {
  const { t } = useI18n()
  const [columns, setColumns] = useState<Set<number>>(() => new Set(dataset.columns.map((_, i) => i)))
  const [mode, setMode] = useState<Mode>('exact')
  const [ignoreCaseAndSpaces, setIgnoreCaseAndSpaces] = useState(false)
  const [similarSettings, setSimilarSettings] = useStoredState('datacleanr.similarRows', defaultSimilarSettings)
  // Filling empty cells only adds data, so it is on by default (and previewed per group)
  const [merge, setMerge] = useStoredState('datacleanr.mergeDuplicates', () => true)
  // Per group: which row to keep (default: the first one) and whether the user flipped its inclusion.
  // Exact duplicates are included by default; possible duplicates must be confirmed one by one.
  const [kept, setKept] = useState<Record<number, number>>({})
  const [flipped, setFlipped] = useState<Set<number>>(new Set())
  const isIncluded = (group: number) => (mode === 'exact') !== flipped.has(group)

  const tooManyRows = mode === 'similar' && dataset.rows.length > MAX_ROWS_FOR_SIMILAR
  const groups = useMemo<Group[]>(() => {
    const sortedColumns = [...columns].sort((a, b) => a - b)
    if (mode === 'exact') {
      return findDuplicateRows(dataset.rows, { columns: sortedColumns, ignoreCaseAndSpaces }).map((rows) => ({ rows }))
    }
    if (tooManyRows) return []
    return findSimilarRows(dataset.rows, { columns: sortedColumns, ...similarSettings })
  }, [dataset, columns, mode, ignoreCaseAndSpaces, similarSettings, tooManyRows])
  // Indexed like `groups`; null for groups that are not included
  const plans = useMemo<(GroupPlan | null)[]>(
    () =>
      groups.map(({ rows }, g) => {
        if ((mode === 'exact') === flipped.has(g)) return null
        const keep = kept[g] ?? rows[0]
        const merged = merge ? mergeRows(rows.map((row) => dataset.rows[row]), rows.indexOf(keep)) : null
        return { keep, remove: rows.filter((row) => row !== keep), merged }
      }),
    [groups, kept, flipped, mode, merge, dataset],
  )
  const toRemove = new Set(plans.flatMap((plan) => plan?.remove ?? []))
  const filledCount = plans.reduce((sum, plan) => sum + (plan?.merged?.filled.length ?? 0), 0)

  function apply() {
    const rows = [...dataset.rows]
    for (const plan of plans) if (plan?.merged) rows[plan.keep] = plan.merged.row
    const step: ProfileStep | null =
      mode === 'exact'
        ? {
            type: 'removeDuplicates',
            columns: [...columns].sort((a, b) => a - b).map((c) => dataset.columns[c]),
            ignoreCaseAndSpaces,
            merge,
          }
        : null
    onRemove(removeRows({ ...dataset, rows }, toRemove), toRemove.size, mode, filledCount, step)
  }

  function resetChoices() {
    setKept({})
    setFlipped(new Set())
  }

  function changeMode(next: Mode) {
    setMode(next)
    resetChoices()
  }

  function toggleColumn(column: number) {
    const next = new Set(columns)
    if (next.has(column)) next.delete(column)
    else next.add(column)
    setColumns(next)
    resetChoices()
  }

  function toggleGroup(group: number) {
    const next = new Set(flipped)
    if (next.has(group)) next.delete(group)
    else next.add(group)
    setFlipped(next)
  }

  return (
    <section className="panel duplicates">
      <div className="duplicates__header">
        <h2 className="transform-panel__title">{t.duplicatesTitle}</h2>
        <button type="button" className="button" onClick={onClose}>
          {t.close}
        </button>
      </div>

      <div className="duplicates__modes" role="group" aria-label={t.duplicatesMode}>
        <button type="button" className="button" aria-pressed={mode === 'exact'} onClick={() => changeMode('exact')}>
          {t.duplicatesExact}
        </button>
        <button type="button" className="button" aria-pressed={mode === 'similar'} onClick={() => changeMode('similar')}>
          {t.duplicatesSimilar}
        </button>
      </div>

      <div className="duplicates__options">
        <span className="duplicates__label">{mode === 'exact' ? t.duplicatesCompare : t.duplicatesCompareSimilar}</span>
        <div className="duplicates__columns">
          {dataset.columns.map((_, i) => (
            <button key={i} type="button" className="tag" aria-pressed={columns.has(i)} onClick={() => toggleColumn(i)}>
              {columnLabel(dataset, i)}
            </button>
          ))}
        </div>
        {mode === 'exact' ? (
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
        ) : (
          <div className="similar__options">
            <label className="similar__threshold">
              <span>{t.similarThreshold(similarSettings.threshold)}</span>
              <input
                type="range"
                min={70}
                max={100}
                value={similarSettings.threshold}
                onChange={(event) => {
                  setSimilarSettings({ ...similarSettings, threshold: Number(event.target.value) })
                  resetChoices()
                }}
              />
            </label>
            <label className="transform-panel__check">
              <input
                type="checkbox"
                checked={similarSettings.ignoreLegalForms}
                onChange={(event) => {
                  setSimilarSettings({ ...similarSettings, ignoreLegalForms: event.target.checked })
                  resetChoices()
                }}
              />
              {t.similarIgnoreLegalForms}
            </label>
          </div>
        )}
        <label className="transform-panel__check">
          <input type="checkbox" checked={merge} onChange={(event) => setMerge(event.target.checked)} />
          {t.duplicatesMerge}
        </label>
        <p className="transform-panel__hint">{mode === 'exact' ? t.duplicatesHint : t.duplicatesSimilarHint}</p>
      </div>

      {tooManyRows && (
        <p className="transform-panel__warning">{t.duplicatesTooManyRows(dataset.rows.length, MAX_ROWS_FOR_SIMILAR)}</p>
      )}
      {columns.size === 0 && <p className="transform-panel__info">{t.duplicatesNoColumns}</p>}
      {columns.size > 0 && !tooManyRows && groups.length === 0 && (
        <p className="transform-panel__info">{t.duplicatesNone}</p>
      )}

      {groups.length > 0 && (
        <>
          <ul className="duplicates__groups">
            {groups.slice(0, MAX_VISIBLE_GROUPS).map(({ rows: group, scores }, g) => {
              const keep = kept[g] ?? group[0]
              const isExcluded = !isIncluded(g)
              const merged = plans[g]?.merged
              return (
                <li key={group[0]} className={`duplicates__group${isExcluded ? ' duplicates__group--excluded' : ''}`}>
                  <label className="transform-panel__check duplicates__group-title">
                    <input type="checkbox" checked={!isExcluded} onChange={() => toggleGroup(g)} />
                    {scores ? t.duplicatesSimilarGroup(group.length) : t.duplicatesGroup(group.length)}
                  </label>
                  <div className="duplicates__scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>{t.duplicatesKeep}</th>
                          <th>#</th>
                          {scores && <th>{t.duplicatesScore}</th>}
                          {dataset.columns.map((_, c) => (
                            <th key={c} aria-selected={columns.has(c)}>
                              {columnLabel(dataset, c)}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {group.map((row, i) => (
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
                            {scores && <td className="duplicates__score">{i === 0 ? '—' : `${Math.floor(scores[i])}%`}</td>}
                            {dataset.rows[row].map((cell, c) => (
                              <td key={c} aria-selected={columns.has(c)}>
                                <VisibleText value={cell} />
                              </td>
                            ))}
                          </tr>
                        ))}
                        {merged && merged.filled.length > 0 && (
                          <tr className="duplicates__result">
                            <td colSpan={scores ? 3 : 2}>{t.duplicatesResult}</td>
                            {merged.row.map((cell, c) => {
                              const isFilled = merged.filled.includes(c)
                              const isConflict = merged.conflicts.includes(c)
                              return (
                                <td
                                  key={c}
                                  className={isConflict ? 'duplicates__conflict' : isFilled ? 'duplicates__filled' : undefined}
                                  title={isConflict ? t.duplicatesConflict : undefined}
                                >
                                  <VisibleText value={cell} />
                                </td>
                              )
                            })}
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </li>
              )
            })}
          </ul>
          {groups.length > MAX_VISIBLE_GROUPS && (
            <p className="transform-panel__info">
              {mode === 'exact'
                ? t.duplicatesTruncated(MAX_VISIBLE_GROUPS, groups.length)
                : t.duplicatesSimilarTruncated(MAX_VISIBLE_GROUPS, groups.length)}
            </p>
          )}
          <div className="transform-panel__actions">
            <span className="transform-panel__info">
              {t.duplicatesSummary(groups.length, toRemove.size)}
              {filledCount > 0 && ` · ${t.duplicatesFilled(filledCount)}`}
            </span>
            <button type="button" className="button button--primary" disabled={toRemove.size === 0} onClick={apply}>
              {t.duplicatesRemove(toRemove.size)}
            </button>
          </div>
        </>
      )}
    </section>
  )
}
