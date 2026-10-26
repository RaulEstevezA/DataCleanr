import { useId, useMemo, useState } from 'react'
import { applyColumnChanges, previewColumnChanges } from '../core/changes.ts'
import { columnLabel, type Dataset } from '../core/dataset.ts'
import { createReplaceTransform, type ReplaceOptions } from '../core/replace.ts'
import { transformIds, transforms, type TransformId } from '../core/transforms.ts'
import { useI18n } from '../i18n/useI18n.ts'
import { VisibleText } from './VisibleText.tsx'
import './TransformPanel.css'

// Rendering thousands of rows at once would freeze the page
const MAX_PREVIEW_ROWS = 200

type Selection = TransformId | 'custom'

const initialReplace: ReplaceOptions = { find: '', replacement: '', wholeCell: true, ignoreCase: true }

interface TransformPanelProps {
  dataset: Dataset
  column: number
  onApply: (dataset: Dataset, appliedCount: number) => void
}

export function TransformPanel({ dataset, column, onApply }: TransformPanelProps) {
  const { t, language } = useI18n()
  const [transformId, setTransformId] = useState<Selection | null>(null)
  const [replace, setReplace] = useState<ReplaceOptions>(initialReplace)
  // Store rejections (not acceptances) so every change is accepted by default
  const [rejected, setRejected] = useState<Set<number>>(new Set())

  const changes = useMemo(() => {
    if (!transformId) return []
    const transform = transformId === 'custom' ? createReplaceTransform(replace) : transforms[transformId]
    return previewColumnChanges(dataset, column, transform)
  }, [dataset, column, transformId, replace])
  // Distinct values of the column, offered as suggestions in the "find" field
  const columnValues = useMemo(
    () => [...new Set(dataset.rows.map((row) => row[column].trim()))].filter(Boolean).sort(),
    [dataset, column],
  )
  const ids = useId()
  const accepted = changes.filter((change) => !rejected.has(change.row))
  const format = (n: number) => n.toLocaleString(language)

  function selectTransform(id: Selection) {
    setTransformId(id)
    setRejected(new Set())
  }

  function updateReplace(patch: Partial<ReplaceOptions>) {
    setReplace({ ...replace, ...patch })
    setRejected(new Set())
  }

  function toggleRow(row: number) {
    const next = new Set(rejected)
    if (next.has(row)) next.delete(row)
    else next.add(row)
    setRejected(next)
  }

  function toggleAll() {
    setRejected(rejected.size === 0 ? new Set(changes.map((change) => change.row)) : new Set())
  }

  function apply() {
    onApply(applyColumnChanges(dataset, column, accepted), accepted.length)
    setTransformId(null)
    setReplace(initialReplace)
    setRejected(new Set())
  }

  return (
    <section className="panel transform-panel">
      <h2 className="transform-panel__title">{t.cleanColumn(columnLabel(dataset, column))}</h2>

      <div className="transform-panel__options" role="group" aria-label={t.transformLabel}>
        {transformIds.map((id) => (
          <button
            key={id}
            type="button"
            className="button"
            aria-pressed={id === transformId}
            onClick={() => selectTransform(id)}
          >
            {t.transformNames[id]}
          </button>
        ))}
        <button
          type="button"
          className="button"
          aria-pressed={transformId === 'custom'}
          onClick={() => selectTransform('custom')}
        >
          {t.customReplace}
        </button>
      </div>

      {transformId === 'custom' && (
        <div className="transform-panel__custom">
          <label>
            <span>{t.findLabel}</span>
            <input
              type="text"
              list={`${ids}-values`}
              value={replace.find}
              placeholder={t.findPlaceholder}
              onChange={(event) => updateReplace({ find: event.target.value })}
            />
            <datalist id={`${ids}-values`}>
              {columnValues.map((value) => (
                <option key={value} value={value} />
              ))}
            </datalist>
          </label>
          <label>
            <span>{t.replaceLabel}</span>
            <input
              type="text"
              value={replace.replacement}
              placeholder={t.replacePlaceholder}
              onChange={(event) => updateReplace({ replacement: event.target.value })}
            />
          </label>
          <div className="transform-panel__custom-options">
            <label className="transform-panel__check">
              <input
                type="checkbox"
                checked={replace.wholeCell}
                onChange={(event) => updateReplace({ wholeCell: event.target.checked })}
              />
              {t.wholeCell}
            </label>
            <label className="transform-panel__check">
              <input
                type="checkbox"
                checked={replace.ignoreCase}
                onChange={(event) => updateReplace({ ignoreCase: event.target.checked })}
              />
              {t.ignoreCase}
            </label>
          </div>
        </div>
      )}

      {transformId && changes.length === 0 && (transformId !== 'custom' || replace.find.trim() !== '') && (
        <p className="transform-panel__info">{transformId === 'custom' ? t.noMatches : t.noChanges}</p>
      )}

      {changes.length > 0 && (
        <>
          <div className="transform-panel__preview">
            <table>
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      aria-label={t.toggleAll}
                      checked={rejected.size === 0}
                      ref={(input) => {
                        if (input) input.indeterminate = rejected.size > 0 && rejected.size < changes.length
                      }}
                      onChange={toggleAll}
                    />
                  </th>
                  <th>#</th>
                  <th>{t.original}</th>
                  <th aria-hidden="true" />
                  <th>{t.proposed}</th>
                </tr>
              </thead>
              <tbody>
                {changes.slice(0, MAX_PREVIEW_ROWS).map((change) => {
                  const isAccepted = !rejected.has(change.row)
                  return (
                    <tr key={change.row} className={isAccepted ? undefined : 'transform-panel__rejected'}>
                      <td>
                        <input
                          type="checkbox"
                          aria-label={t.acceptRow(format(change.row + 1))}
                          checked={isAccepted}
                          onChange={() => toggleRow(change.row)}
                        />
                      </td>
                      <td className="transform-panel__index">{change.row + 1}</td>
                      <td className="transform-panel__original">
                        <VisibleText value={change.original} />
                      </td>
                      <td className="transform-panel__arrow" aria-hidden="true">
                        →
                      </td>
                      <td className="transform-panel__proposed">
                        <VisibleText value={change.proposed} />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          {changes.length > MAX_PREVIEW_ROWS && (
            <p className="transform-panel__info">
              {t.previewTruncated(format(MAX_PREVIEW_ROWS), format(changes.length))}
            </p>
          )}
          <div className="transform-panel__actions">
            <span className="transform-panel__info">
              {t.changesSelected(format(accepted.length), format(changes.length))}
            </span>
            <button type="button" className="button" onClick={() => setTransformId(null)}>
              {t.cancel}
            </button>
            <button type="button" className="button button--primary" disabled={accepted.length === 0} onClick={apply}>
              {t.applyChanges(format(accepted.length))}
            </button>
          </div>
        </>
      )}
    </section>
  )
}
