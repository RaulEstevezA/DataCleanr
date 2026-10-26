/** Cell type chosen by the user for each column when exporting to Excel. */
export type ColumnType = 'text' | 'number' | 'date' | 'boolean'

export type TypedCell =
  | { type: 'empty' }
  | { type: 'text'; value: string }
  | { type: 'number'; value: number }
  /** ISO text: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS" */
  | { type: 'date'; value: string }
  | { type: 'boolean'; value: boolean }

// Plain dot-decimal numbers without leading zeros: what "Normalize amounts" produces
const NUMBER = /^-?(0|[1-9]\d*)(\.\d+)?$/
const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})(?: (\d{2}):(\d{2}):(\d{2}))?$/
// Excel (like JavaScript and Python floats) keeps 15 significant digits safely
const MAX_SIGNIFICANT_DIGITS = 15

function toNumber(value: string): number | null {
  if (!NUMBER.test(value)) return null
  const significant = value.replace('-', '').replace('.', '').replace(/^0+/, '')
  const [, decimals = ''] = value.split('.')
  const trailingZeros = decimals.length - decimals.replace(/0+$/, '').length
  return significant.length - trailingZeros > MAX_SIGNIFICANT_DIGITS ? null : Number(value)
}

function isIsoDate(value: string): boolean {
  const match = ISO_DATE.exec(value)
  if (!match) return false
  const [year, month, day, hours = 0, minutes = 0, seconds = 0] = match
    .slice(1)
    .filter((part) => part !== undefined)
    .map(Number)
  // Round-trip through Date: impossible dates (Feb 29 2023, 25:00...) come back different
  const date = new Date(Date.UTC(year, month - 1, day, hours, minutes, seconds))
  return (
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day &&
    date.getUTCHours() === hours &&
    date.getUTCMinutes() === minutes &&
    date.getUTCSeconds() === seconds
  )
}

function toBoolean(value: string): boolean | null {
  const lower = value.toLowerCase()
  return lower === 'true' ? true : lower === 'false' ? false : null
}

/**
 * Converts a cell to the requested type. Values that cannot be converted without
 * changing or losing information (leading zeros, comma decimals, non-ISO dates...)
 * stay as text, so the user never loses data by picking the wrong type.
 */
export function toTypedCell(value: string, type: ColumnType): TypedCell {
  if (value === '') return { type: 'empty' }
  if (type === 'number') {
    const number = toNumber(value)
    if (number !== null) return { type: 'number', value: number }
  }
  if (type === 'date' && isIsoDate(value)) return { type: 'date', value }
  if (type === 'boolean') {
    const boolean = toBoolean(value)
    if (boolean !== null) return { type: 'boolean', value: boolean }
  }
  return { type: 'text', value }
}

/** Number of non-empty values that would stay as text with the given type. */
export function countTextFallbacks(values: string[], type: ColumnType): number {
  if (type === 'text') return 0
  return values.filter((value) => toTypedCell(value, type).type === 'text').length
}

/** Suggests a type: the first of boolean, date, number that fits every non-empty value; text otherwise. */
export function suggestColumnType(values: string[]): ColumnType {
  const filled = values.filter((value) => value !== '')
  if (filled.length === 0) return 'text'
  for (const type of ['boolean', 'date', 'number'] as const) {
    if (countTextFallbacks(filled, type) === 0) return type
  }
  return 'text'
}
