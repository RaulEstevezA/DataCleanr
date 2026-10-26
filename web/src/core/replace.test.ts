import { describe, expect, it } from 'vitest'
import { createReplaceTransform } from './replace.ts'

const options = { find: 'Transgrau s.l', replacement: 'TransGrau SL', wholeCell: true, ignoreCase: true }

describe('createReplaceTransform (whole cell)', () => {
  const replace = createReplaceTransform(options)

  it('replaces a matching cell ignoring case', () => {
    expect(replace('TRANSGRAU S.L')).toBe('TransGrau SL')
  })

  it('ignores surrounding spaces in the cell', () => {
    expect(replace('  Transgrau s.l ')).toBe('TransGrau SL')
  })

  it('does not touch cells that only contain the text', () => {
    expect(replace('Transgrau s.l.')).toBe('Transgrau s.l.')
  })

  it('respects case when ignoreCase is false', () => {
    const strict = createReplaceTransform({ ...options, ignoreCase: false })
    expect(strict('TRANSGRAU S.L')).toBe('TRANSGRAU S.L')
    expect(strict('Transgrau s.l')).toBe('TransGrau SL')
  })
})

describe('createReplaceTransform (part of text)', () => {
  const replace = createReplaceTransform({ ...options, find: 's.l.', replacement: 'S.L.', wholeCell: false })

  it('replaces every occurrence inside the text', () => {
    expect(replace('Transgrau s.l. y Frutas s.l.')).toBe('Transgrau S.L. y Frutas S.L.')
  })

  it('treats special characters literally', () => {
    expect(replace('Transgrau sXlX')).toBe('Transgrau sXlX')
  })

  it('inserts "$" in the replacement literally', () => {
    const dollars = createReplaceTransform({ ...options, find: 'EUR', replacement: '$&', wholeCell: false })
    expect(dollars('100 EUR')).toBe('100 $&')
  })
})

describe('createReplaceTransform (empty search)', () => {
  it('changes nothing', () => {
    const replace = createReplaceTransform({ ...options, find: '  ' })
    expect(replace('Transgrau')).toBe('Transgrau')
    expect(replace('')).toBe('')
  })
})
