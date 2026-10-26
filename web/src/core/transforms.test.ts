import { describe, expect, it } from 'vitest'
import { transforms } from './transforms.ts'

describe('trim', () => {
  it('removes leading and trailing whitespace', () => {
    expect(transforms.trim('  TRANSGRAU ')).toBe('TRANSGRAU')
  })

  it('removes tabs and non-breaking spaces at the edges', () => {
    expect(transforms.trim('\t Valencia ')).toBe('Valencia')
  })

  it('keeps inner spaces', () => {
    expect(transforms.trim(' laura   NAVARRO ')).toBe('laura   NAVARRO')
  })
})

describe('collapseSpaces', () => {
  it('turns repeated spaces into one', () => {
    expect(transforms.collapseSpaces('laura   NAVARRO')).toBe('laura NAVARRO')
  })

  it('normalizes tabs and non-breaking spaces', () => {
    expect(transforms.collapseSpaces('Trans\t Grau')).toBe('Trans Grau')
  })

  it('does not trim the edges', () => {
    expect(transforms.collapseSpaces('  ana   ruiz ')).toBe(' ana ruiz ')
  })
})

describe('lowercase', () => {
  it('lowercases accented letters', () => {
    expect(transforms.lowercase('MARÍA LÓPEZ')).toBe('maría lópez')
  })
})

describe('uppercase', () => {
  it('uppercases accented letters and ñ', () => {
    expect(transforms.uppercase('logística españa')).toBe('LOGÍSTICA ESPAÑA')
  })
})

describe('titleCase', () => {
  it('capitalizes each word', () => {
    expect(transforms.titleCase('laura NAVARRO')).toBe('Laura Navarro')
  })

  it('handles accented first letters', () => {
    expect(transforms.titleCase('ángel ÚBEDA')).toBe('Ángel Úbeda')
  })

  it('capitalizes after hyphens', () => {
    expect(transforms.titleCase('jean-luc PÉREZ')).toBe('Jean-Luc Pérez')
  })

  it('preserves surrounding whitespace', () => {
    expect(transforms.titleCase('  ana   ruiz ')).toBe('  Ana   Ruiz ')
  })

  it('does not capitalize after digits or dots', () => {
    expect(transforms.titleCase('calle 3b s.l.')).toBe('Calle 3b S.l.')
  })
})

describe('all transforms', () => {
  it('leave empty strings empty', () => {
    for (const transform of Object.values(transforms)) {
      expect(transform('')).toBe('')
    }
  })
})
