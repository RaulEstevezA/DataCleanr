import { useId } from 'react'
import type { DateFormat, DateInputOrder, DateOptions } from '../core/date.ts'
import { useI18n } from '../i18n/useI18n.ts'

const inputOrders: { id: DateInputOrder; example: string }[] = [
  { id: 'DMY', example: '13/07/2024' },
  { id: 'MDY', example: '07/13/2024' },
]

const formats: { id: DateFormat; example: string }[] = [
  { id: 'ISO', example: '2024-07-13' },
  { id: 'DMY', example: '13/07/2024' },
  { id: 'MDY', example: '07/13/2024' },
]

interface DateFormProps {
  options: DateOptions
  onChange: (options: DateOptions) => void
}

export function DateForm({ options, onChange }: DateFormProps) {
  const { t } = useI18n()
  const limitId = useId()
  const limit = options.twoDigitYearLimit
  const pad = (n: number) => String(n).padStart(2, '0')

  function changeLimit(text: string) {
    const value = Number.parseInt(text, 10)
    if (Number.isNaN(value)) return
    onChange({ ...options, twoDigitYearLimit: Math.min(99, Math.max(0, value)) })
  }

  return (
    <div className="transform-panel__custom">
      <fieldset className="transform-panel__formats">
        <legend>{t.dateInputOrder}</legend>
        {inputOrders.map(({ id, example }) => (
          <label key={id} className="transform-panel__check">
            <input
              type="radio"
              name="date-input-order"
              checked={options.inputOrder === id}
              onChange={() => onChange({ ...options, inputOrder: id })}
            />
            {t.dateOrderNames[id]}
            <code>{example}</code>
          </label>
        ))}
      </fieldset>
      <fieldset className="transform-panel__formats">
        <legend>{t.dateFormat}</legend>
        {formats.map(({ id, example }) => (
          <label key={id} className="transform-panel__check">
            <input
              type="radio"
              name="date-format"
              checked={options.format === id}
              onChange={() => onChange({ ...options, format: id })}
            />
            {t.dateFormatNames[id]}
            <code>{example}</code>
          </label>
        ))}
      </fieldset>
      <div className="transform-panel__year-limit">
        <label htmlFor={limitId}>{t.dateTwoDigitLimit}</label>
        <div className="transform-panel__year-limit-input">
          <span>00 –</span>
          <input
            id={limitId}
            type="number"
            min={0}
            max={99}
            value={limit}
            onChange={(event) => changeLimit(event.target.value)}
          />
          <span>→ 20xx</span>
        </div>
        <p className="transform-panel__hint">
          {limit === 99
            ? '00–99 → 2000–2099'
            : `00–${pad(limit)} → 2000–20${pad(limit)} · ${pad(limit + 1)}–99 → 19${pad(limit + 1)}–1999`}
        </p>
      </div>
      <p className="transform-panel__hint">{t.dateHint}</p>
    </div>
  )
}
