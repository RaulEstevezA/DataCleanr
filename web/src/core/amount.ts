/** Decimal separator assumed when a value is ambiguous, like "1.234" or "1,234". */
export type DecimalSeparator = ',' | '.'

/** DOT: 1234.56 · COMMA: 1234,56 · DOT_GROUPED: 1,234.56 · COMMA_GROUPED: 1.234,56 */
export type AmountFormat = 'DOT' | 'COMMA' | 'DOT_GROUPED' | 'COMMA_GROUPED'

export interface AmountOptions {
  ambiguousDecimal: DecimalSeparator
  format: AmountFormat
  /** Pad to exactly two decimals. Values with more decimals are never rounded: they go to review. */
  twoDecimals: boolean
}

export type AmountStatus = 'valid' | 'invalid' | 'empty'

export interface AmountResult {
  status: AmountStatus
  /** Formatted number when valid; the untouched input otherwise. */
  value: string
  /** Currency found next to the number (removed from the output), if any. */
  currency?: string | null
}

const CURRENCIES: Record<string, string> = { '€': 'EUR', EUR: 'EUR', $: 'USD', USD: 'USD', '£': 'GBP', GBP: 'GBP' }
const CURRENCY = '(€|\\$|£|EUR|USD|GBP)'
// Thousands separators other than "." and ",": spaces (regular, non-breaking, narrow) and the Swiss apostrophe
const EXTRA_GROUP = "   '"
const AMOUNT = new RegExp(
  `^([-+])?\\s*${CURRENCY}?\\s*([-+])?\\s*([0-9.,${EXTRA_GROUP}]+?)\\s*${CURRENCY}?$`,
  'i',
)

interface ParsedAmount {
  negative: boolean
  integer: string
  decimals: string
  currency: string | null
}

/** Picks which separator (if any) is the decimal one. Returns undefined when the value is malformed. */
function findDecimalSeparator(body: string, ambiguousDecimal: DecimalSeparator): string | null | undefined {
  const dots = body.split('.').length - 1
  const commas = body.split(',').length - 1

  if (dots > 0 && commas > 0) {
    // Both present: the last one is the decimal separator and must appear once
    const decimal = body.lastIndexOf('.') > body.lastIndexOf(',') ? '.' : ','
    return (decimal === '.' ? dots : commas) === 1 ? decimal : undefined
  }
  if (dots + commas === 0) return null

  const separator = dots > 0 ? '.' : ','
  // Repeated separator can only be thousands: 1.234.567
  if (dots + commas > 1) return null

  const [before, after] = body.split(separator)
  const beforeDigits = before.replace(/\D/g, '')
  const hasOtherGrouping = /[^\d]/.test(before)
  // Only "1-3 digits, separator, exactly 3 digits" (1.234) could be either: use the user's choice
  const couldBeThousands =
    after.length === 3 && beforeDigits.length >= 1 && beforeDigits.length <= 3 && !beforeDigits.startsWith('0')
  if (!couldBeThousands || hasOtherGrouping) return separator
  return separator === ambiguousDecimal ? separator : null
}

function parseAmount(value: string, ambiguousDecimal: DecimalSeparator): ParsedAmount | null {
  let text = value.trim()
  let negative = false
  const parenthesized = /^\((.*)\)$/.exec(text)
  if (parenthesized) {
    negative = true
    text = parenthesized[1].trim()
  }

  const match = AMOUNT.exec(text)
  if (!match) return null
  const [, signBefore, currencyBefore, signAfter, rawBody, currencyAfter] = match
  if ((signBefore && signAfter) || (currencyBefore && currencyAfter)) return null
  const sign = signBefore ?? signAfter
  if (sign && parenthesized) return null
  if (sign === '-') negative = true

  const body = rawBody.trim()
  const decimalSeparator = findDecimalSeparator(body, ambiguousDecimal)
  if (decimalSeparator === undefined) return null

  const [integerPart, decimals = ''] = decimalSeparator ? body.split(decimalSeparator) : [body]
  if (decimalSeparator && !/^\d+$/.test(decimals)) return null

  // Thousands groups: first group 1-3 digits, the rest exactly 3, a single kind of separator
  const groups = integerPart.split(/[.,\s  ']/)
  const separatorsUsed = new Set(integerPart.replace(/\d/g, ''))
  if (separatorsUsed.size > 1) return null
  if (groups.length > 1 && (!/^\d{1,3}$/.test(groups[0]) || groups.slice(1).some((g) => !/^\d{3}$/.test(g)))) {
    return null
  }
  const digits = groups.join('')
  if (!/^\d*$/.test(digits) || (digits === '' && decimals === '')) return null

  const code = (currencyBefore ?? currencyAfter)?.toUpperCase()
  return {
    negative,
    integer: digits.replace(/^0+(?=\d)/, '') || '0',
    decimals,
    currency: code ? CURRENCIES[code] : null,
  }
}

const groupThousands = (integer: string, separator: string) => integer.replace(/\B(?=(\d{3})+(?!\d))/g, separator)

/**
 * Normalizes one amount. Works on the digits as text (never as a floating-point number)
 * so no precision is lost. Anything malformed or ambiguous goes to review unchanged.
 */
export function normalizeAmount(value: string, { ambiguousDecimal, format, twoDecimals }: AmountOptions): AmountResult {
  if (value.trim() === '') return { status: 'empty', value }

  const parsed = parseAmount(value, ambiguousDecimal)
  if (!parsed) return { status: 'invalid', value }

  let { decimals } = parsed
  if (twoDecimals) {
    if (decimals.length > 2) return { status: 'invalid', value }
    decimals = decimals.padEnd(2, '0')
  }

  const decimalSeparator = format === 'DOT' || format === 'DOT_GROUPED' ? '.' : ','
  const integer =
    format === 'DOT_GROUPED'
      ? groupThousands(parsed.integer, ',')
      : format === 'COMMA_GROUPED'
        ? groupThousands(parsed.integer, '.')
        : parsed.integer

  const formatted = `${parsed.negative ? '-' : ''}${integer}${decimals ? decimalSeparator + decimals : ''}`
  return { status: 'valid', value: formatted, currency: parsed.currency }
}

export function createAmountTransform(options: AmountOptions) {
  return (value: string) => normalizeAmount(value, options).value
}
