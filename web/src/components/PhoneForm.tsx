import { useMemo } from 'react'
import type { CountryCode } from 'libphonenumber-js/max'
import type { PhoneFormat, PhoneOptions } from '../core/phone.ts'
import { useI18n } from '../i18n/useI18n.ts'

const formats: { id: PhoneFormat; example: string }[] = [
  { id: 'E164', example: '+34600123456' },
  { id: 'INTERNATIONAL', example: '+34 600 12 34 56' },
  { id: 'NATIONAL', example: '600 12 34 56' },
]

interface PhoneFormProps {
  options: PhoneOptions
  countries: CountryCode[]
  onChange: (options: PhoneOptions) => void
}

export function PhoneForm({ options, countries, onChange }: PhoneFormProps) {
  const { t, language } = useI18n()

  const sortedCountries = useMemo(() => {
    const names = new Intl.DisplayNames([language], { type: 'region' })
    return countries
      .map((code) => ({ code, name: names.of(code) ?? code }))
      .sort((a, b) => a.name.localeCompare(b.name, language))
  }, [countries, language])

  return (
    <div className="transform-panel__custom">
      <label>
        <span>{t.phoneCountry}</span>
        <select
          value={options.defaultCountry}
          onChange={(event) => onChange({ ...options, defaultCountry: event.target.value as CountryCode })}
        >
          {sortedCountries.map(({ code, name }) => (
            <option key={code} value={code}>
              {name}
            </option>
          ))}
        </select>
      </label>
      <fieldset className="transform-panel__formats">
        <legend>{t.phoneFormat}</legend>
        {formats.map(({ id, example }) => (
          <label key={id} className="transform-panel__check">
            <input
              type="radio"
              name="phone-format"
              checked={options.format === id}
              onChange={() => onChange({ ...options, format: id })}
            />
            {t.phoneFormatNames[id]}
            <code>{example}</code>
          </label>
        ))}
      </fieldset>
      <p className="transform-panel__hint">{t.phoneHint}</p>
    </div>
  )
}
