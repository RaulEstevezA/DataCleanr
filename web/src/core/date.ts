/** How to read ambiguous dates like 03/04/2024. Year-first dates are always year/month/day. */
export type DateInputOrder = 'DMY' | 'MDY'

export type DateFormat = 'ISO' | 'DMY' | 'MDY'

export interface DateOptions {
  inputOrder: DateInputOrder
  format: DateFormat
  /** Two-digit years from 00 up to this value are 20xx; above it, 19xx. Excel uses 29. */
  twoDigitYearLimit: number
}

export const DEFAULT_TWO_DIGIT_YEAR_LIMIT = 29

export type DateStatus = 'valid' | 'invalid' | 'empty'

export interface DateResult {
  status: DateStatus
  /** Formatted date when valid; the untouched input otherwise. */
  value: string
}

// \2 forces the same separator throughout: "13/07-2024" is rejected
const YEAR_FIRST = /^(\d{4})([-/.])(\d{1,2})\2(\d{1,2})$/
const YEAR_LAST = /^(\d{1,2})([-/.])(\d{1,2})\2(\d{2}|\d{4})$/

function expandYear(year: string, limit: number): number {
  const value = Number(year)
  if (year.length === 4) return value
  return value <= limit ? 2000 + value : 1900 + value
}

const isLeapYear = (year: number) => (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0

const DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

/** Plain calendar arithmetic: JavaScript's Date maps years 0-99 to 1900-1999, which would break year 0 and leap days. */
function isRealDate(year: number, month: number, day: number): boolean {
  if (year < 1 || month < 1 || month > 12 || day < 1) return false
  const daysInMonth = month === 2 && isLeapYear(year) ? 29 : DAYS_IN_MONTH[month - 1]
  return day <= daysInMonth
}

const pad = (value: number, length = 2) => String(value).padStart(length, '0')

/**
 * Normalizes one date. Anything ambiguous or unsupported (times, month names...)
 * is returned unchanged with status "invalid" so the user can review it by hand.
 */
export function normalizeDate(value: string, { inputOrder, format, twoDigitYearLimit }: DateOptions): DateResult {
  const text = value.trim()
  if (text === '') return { status: 'empty', value }

  let year: number, month: number, day: number
  const yearFirst = YEAR_FIRST.exec(text)
  const yearLast = YEAR_LAST.exec(text)
  if (yearFirst) {
    year = Number(yearFirst[1])
    month = Number(yearFirst[3])
    day = Number(yearFirst[4])
  } else if (yearLast) {
    const [first, second] = [Number(yearLast[1]), Number(yearLast[3])]
    ;[day, month] = inputOrder === 'DMY' ? [first, second] : [second, first]
    year = expandYear(yearLast[4], twoDigitYearLimit)
  } else {
    return { status: 'invalid', value }
  }

  if (!isRealDate(year, month, day)) return { status: 'invalid', value }

  const formatted = {
    ISO: `${pad(year, 4)}-${pad(month)}-${pad(day)}`,
    DMY: `${pad(day)}/${pad(month)}/${pad(year, 4)}`,
    MDY: `${pad(month)}/${pad(day)}/${pad(year, 4)}`,
  }[format]
  return { status: 'valid', value: formatted }
}

export function createDateTransform(options: DateOptions) {
  return (value: string) => normalizeDate(value, options).value
}
