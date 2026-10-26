import type { Profile, StepResult } from '../core/profile.ts'
import { useI18n } from '../i18n/useI18n.ts'
import { describeProfileStep } from './profileLabels.ts'
import './ProfilePanel.css'

interface ProfilePanelProps {
  profile: Profile
  results: StepResult[]
  onApply: () => void
  onClose: () => void
}

/** Preview of a profile run: what each step would do before anything is applied. */
export function ProfilePanel({ profile, results, onApply, onClose }: ProfilePanelProps) {
  const { t } = useI18n()
  const effective = results.filter((result) => result.status === 'applied' && result.count > 0)

  return (
    <section className="panel profile">
      <div className="duplicates__header">
        <h2 className="transform-panel__title">{t.profileTitle(profile.name)}</h2>
        <button type="button" className="button" onClick={onClose}>
          {t.close}
        </button>
      </div>
      <p className="transform-panel__hint">{t.profileApplyHint}</p>
      <ol className="profile__steps">
        {results.map((result, i) => (
          <li key={i} className={`profile__step profile__step--${result.status === 'skipped' ? 'skipped' : result.count > 0 ? 'changes' : 'none'}`}>
            <span className="history__number">{i + 1}</span>
            <span className="profile__description">{describeProfileStep(t, result.step)}</span>
            <span className="profile__outcome">
              {result.status === 'skipped'
                ? t.profileSkipped[result.reason ?? 'missingColumn']
                : result.step.type === 'removeDuplicates'
                  ? t.removedRows(result.count)
                  : t.modifiedCells(result.count)}
            </span>
          </li>
        ))}
      </ol>
      <div className="transform-panel__actions">
        <span className="transform-panel__info">{t.profileSummary(effective.length, results.length)}</span>
        <button type="button" className="button button--primary" disabled={effective.length === 0} onClick={onApply}>
          {t.profileApply(effective.length)}
        </button>
      </div>
    </section>
  )
}
