import { getCountries, parsePhoneNumberFromString, type CountryCode } from 'libphonenumber-js/max'

export type PhoneFormat = 'E164' | 'INTERNATIONAL' | 'NATIONAL'

export interface PhoneOptions {
  /** Country assumed for numbers written without an international prefix. */
  defaultCountry: CountryCode
  format: PhoneFormat
}

export type PhoneStatus = 'valid' | 'invalid' | 'empty'

export interface PhoneResult {
  status: PhoneStatus
  /** Normalized number when valid; the untouched input otherwise. */
  value: string
}

export const phoneCountries = getCountries()

/**
 * Normalizes one phone number. Anything that cannot be normalized safely is
 * returned unchanged with status "invalid", so the user can review it by hand.
 */
export function normalizePhone(value: string, { defaultCountry, format }: PhoneOptions): PhoneResult {
  if (value.trim() === '') return { status: 'empty', value }

  const phone = parsePhoneNumberFromString(value.trim(), defaultCountry)
  // E.164 has no room for extensions: converting would silently drop them
  if (!phone?.isValid() || (format === 'E164' && phone.ext)) return { status: 'invalid', value }

  if (format === 'E164') return { status: 'valid', value: phone.number }
  // A national format for a foreign number would lose its country, so keep it international
  if (format === 'NATIONAL' && phone.country === defaultCountry) {
    return { status: 'valid', value: phone.formatNational() }
  }
  return { status: 'valid', value: phone.formatInternational() }
}

export function createPhoneTransform(options: PhoneOptions) {
  return (value: string) => normalizePhone(value, options).value
}
