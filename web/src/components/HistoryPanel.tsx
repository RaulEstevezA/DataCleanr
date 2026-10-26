import { columnLabel, type Dataset } from '../core/dataset.ts'
import type { History } from '../core/history.ts'
import type { CellAction, Operation } from '../core/operation.ts'
import type { Messages } from '../i18n/messages.ts'
import { useI18n } from '../i18n/useI18n.ts'
import './HistoryPanel.css'

export interface HistoryStep {
  dataset: Dataset
  operation: Operation
}

function actionName(t: Messages, action: CellAction): string {
  switch (action) {
    case 'custom':
      return t.customReplace
    case 'phone':
      return t.normalizePhone
    case 'date':
      return t.normalizeDate
    case 'amount':
      return t.normalizeAmount
    case 'similar':
      return t.similarValues
    default:
      return t.transformNames[action]
  }
}

function describe(t: Messages, step: HistoryStep): string {
  const { operation, dataset } = step
  switch (operation.kind) {
    case 'import':
      return t.historyImport(dataset.fileName)
    case 'cells':
      return t.historyCells(actionName(t, operation.action), columnLabel(dataset, operation.column), operation.count)
    case 'removeRows':
      return operation.mode === 'exact'
        ? t.historyRemoveExact(operation.count, operation.filled)
        : t.historyRemoveSimilar(operation.count, operation.filled)
  }
}

interface HistoryPanelProps {
  history: History<HistoryStep>
  onGoTo: (index: number) => void
}

export function HistoryPanel({ history, onGoTo }: HistoryPanelProps) {
  const { t } = useI18n()
  if (history.entries.length < 2) return null

  return (
    <details className="panel history">
      <summary>{t.historyTitle(history.entries.length - 1)}</summary>
      <ol className="history__steps">
        {history.entries.map((step, i) => (
          <li key={i}>
            <button
              type="button"
              className="history__step"
              aria-current={i === history.index ? 'step' : undefined}
              data-undone={i > history.index || undefined}
              onClick={() => onGoTo(i)}
            >
              <span className="history__number">{i}</span>
              {describe(t, step)}
            </button>
          </li>
        ))}
      </ol>
      <p className="transform-panel__hint">{t.historyHint}</p>
    </details>
  )
}
