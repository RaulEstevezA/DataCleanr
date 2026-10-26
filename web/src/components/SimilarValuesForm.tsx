import { useId } from 'react'
import type { SimilarGroup, SimilarOptions } from '../core/similar.ts'
import { useI18n } from '../i18n/useI18n.ts'
import { VisibleText } from './VisibleText.tsx'
import './SimilarValuesForm.css'

/** What the user decided for one group. */
export interface GroupChoice {
  target: string
  custom: boolean
  included: boolean
}

interface SimilarValuesFormProps {
  options: SimilarOptions
  onOptionsChange: (options: SimilarOptions) => void
  groups: SimilarGroup[]
  choices: GroupChoice[]
  onChoiceChange: (index: number, choice: GroupChoice) => void
}

export function SimilarValuesForm({ options, onOptionsChange, groups, choices, onChoiceChange }: SimilarValuesFormProps) {
  const { t } = useI18n()
  const ids = useId()

  return (
    <div className="similar">
      <div className="similar__options">
        <label className="similar__threshold">
          <span>{t.similarThreshold(options.threshold)}</span>
          <input
            type="range"
            min={70}
            max={100}
            value={options.threshold}
            onChange={(event) => onOptionsChange({ ...options, threshold: Number(event.target.value) })}
          />
          <span className="transform-panel__hint">{t.similarThresholdHint}</span>
        </label>
        <label className="transform-panel__check">
          <input
            type="checkbox"
            checked={options.ignoreLegalForms}
            onChange={(event) => onOptionsChange({ ...options, ignoreLegalForms: event.target.checked })}
          />
          {t.similarIgnoreLegalForms}
        </label>
      </div>

      {groups.length === 0 && <p className="transform-panel__info">{t.similarNone}</p>}

      <ul className="similar__groups">
        {groups.map((group, g) => {
          const choice = choices[g]
          const cells = group.variants.reduce((sum, variant) => sum + variant.count, 0)
          return (
            <li key={g} className={`similar__group${choice.included ? '' : ' similar__group--excluded'}`}>
              <label className="similar__include transform-panel__check">
                <input
                  type="checkbox"
                  checked={choice.included}
                  onChange={(event) => onChoiceChange(g, { ...choice, included: event.target.checked })}
                />
                {t.similarGroupSummary(group.variants.length, cells)}
              </label>
              <fieldset disabled={!choice.included}>
                <legend className="similar__legend">{t.similarChooseValue}</legend>
                {group.variants.map((variant) => (
                  <label key={variant.value} className="similar__variant">
                    <input
                      type="radio"
                      name={`${ids}-${g}`}
                      checked={!choice.custom && choice.target === variant.value}
                      onChange={() => onChoiceChange(g, { ...choice, target: variant.value, custom: false })}
                    />
                    <VisibleText value={variant.value} />
                    <span className="similar__count">×{variant.count}</span>
                  </label>
                ))}
                <label className="similar__variant">
                  <input
                    type="radio"
                    name={`${ids}-${g}`}
                    checked={choice.custom}
                    onChange={() => onChoiceChange(g, { ...choice, custom: true, target: '' })}
                  />
                  <span>{t.similarOther}</span>
                  <input
                    type="text"
                    className="similar__custom"
                    placeholder={t.replacePlaceholder}
                    value={choice.custom ? choice.target : ''}
                    onFocus={() => !choice.custom && onChoiceChange(g, { ...choice, custom: true, target: '' })}
                    onChange={(event) => onChoiceChange(g, { ...choice, custom: true, target: event.target.value })}
                  />
                </label>
              </fieldset>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
