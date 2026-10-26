import type { AmountFormat, AmountOptions, DecimalSeparator } from '../core/amount.ts'
import { useI18n } from '../i18n/useI18n.ts'

const separators: { id: DecimalSeparator; example: string }[] = [
  { id: ',', example: '1.234 → 1234' },
  { id: '.', example: '1.234 → 1.234' },
]

const formats: { id: AmountFormat; example: string }[] = [
  { id: 'DOT', example: '1234567.89' },
  { id: 'COMMA', example: '1234567,89' },
  { id: 'COMMA_GROUPED', example: '1.234.567,89' },
  { id: 'DOT_GROUPED', example: '1,234,567.89' },
]

interface AmountFormProps {
  options: AmountOptions
  onChange: (options: AmountOptions) => void
}

export function AmountForm({ options, onChange }: AmountFormProps) {
  const { t } = useI18n()

  return (
    <div className="transform-panel__custom">
      <fieldset className="transform-panel__formats">
        <legend>{t.amountAmbiguous}</legend>
        {separators.map(({ id, example }) => (
          <label key={id} className="transform-panel__check">
            <input
              type="radio"
              name="amount-decimal"
              checked={options.ambiguousDecimal === id}
              onChange={() => onChange({ ...options, ambiguousDecimal: id })}
            />
            {t.amountSeparatorNames[id]}
            <code>{example}</code>
          </label>
        ))}
      </fieldset>
      <fieldset className="transform-panel__formats">
        <legend>{t.amountFormat}</legend>
        {formats.map(({ id, example }) => (
          <label key={id} className="transform-panel__check">
            <input
              type="radio"
              name="amount-format"
              checked={options.format === id}
              onChange={() => onChange({ ...options, format: id })}
            />
            {t.amountFormatNames[id]}
            <code>{example}</code>
          </label>
        ))}
      </fieldset>
      <label className="transform-panel__check">
        <input
          type="checkbox"
          checked={options.twoDecimals}
          onChange={(event) => onChange({ ...options, twoDecimals: event.target.checked })}
        />
        {t.amountTwoDecimals}
      </label>
      <p className="transform-panel__hint">{t.amountHint}</p>
    </div>
  )
}
