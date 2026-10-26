import { useState } from 'react'
import { columnLabel, type Dataset } from '../core/dataset.ts'
import type { History } from '../core/history.ts'
import type { Operation } from '../core/operation.ts'
import { PROFILE_FORMAT, PROFILE_VERSION, serializeProfile, type Profile, type ProfileStep } from '../core/profile.ts'
import { profileFileName } from '../core/profileFile.ts'
import { downloadBlob } from '../utils/download.ts'
import type { Messages } from '../i18n/messages.ts'
import { useI18n } from '../i18n/useI18n.ts'
import { actionName } from './profileLabels.ts'
import './HistoryPanel.css'

export interface HistoryStep {
  dataset: Dataset
  operation: Operation
  /** How to replay this step in a cleaning profile; null when it cannot be replayed. */
  profileStep: ProfileStep | null
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
  const [profileName, setProfileName] = useState('')
  if (history.entries.length < 2) return null

  // Only the steps up to the current one (undone steps are not part of the result)
  const applied = history.entries.slice(1, history.index + 1)
  const replayable = applied.flatMap(({ profileStep }) => (profileStep ? [profileStep] : []))
  const notReplayable = applied.length - replayable.length

  function saveProfile() {
    const name = profileName.trim() || t.profileDefaultName
    const profile: Profile = { format: PROFILE_FORMAT, version: PROFILE_VERSION, name, steps: replayable }
    downloadBlob(new Blob([serializeProfile(profile)], { type: 'application/json' }), profileFileName(name))
  }

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
      <div className="history__save">
        <label>
          <span>{t.profileSaveLabel}</span>
          <input
            type="text"
            value={profileName}
            placeholder={t.profileDefaultName}
            onChange={(event) => setProfileName(event.target.value)}
          />
        </label>
        <button type="button" className="button" disabled={replayable.length === 0} onClick={saveProfile}>
          {t.profileSave(replayable.length)}
        </button>
      </div>
      {notReplayable > 0 && <p className="transform-panel__hint">{t.profileNotReplayable(notReplayable)}</p>}
      <p className="transform-panel__hint">{t.profileSaveHint}</p>
    </details>
  )
}
