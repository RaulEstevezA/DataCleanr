import { describe, expect, it } from 'vitest'
import cases from '../../../shared/test-cases/profile.json'
import type { Dataset } from './dataset.ts'
import { createPhoneTransform } from './phone.ts'
import { parseProfile, ProfileError, runProfile, serializeProfile } from './profile.ts'

describe('runProfile', () => {
  it.each(cases.run)('$description', ({ columns, rows, profile, expected }) => {
    const dataset: Dataset = {
      fileName: 'a.csv',
      format: 'csv',
      sheet: null,
      columns,
      rows,
      rowIds: rows.map((_, i) => i),
      delimiter: ';',
      encoding: 'utf-8',
    }
    const results = runProfile(dataset, parseProfile(JSON.stringify(profile)), { createPhoneTransform })
    expect(results.map(({ status, reason, count }) => (reason ? { status, reason, count } : { status, count }))).toEqual(
      expected.steps,
    )
    const final = results[results.length - 1].dataset
    expect(final.rows).toEqual(expected.rows)
    expect(final.rowIds).toEqual(expected.rowIds)
  })

  it('skips phone steps when phone support is not available', () => {
    const dataset: Dataset = {
      fileName: 'a.csv', format: 'csv', sheet: null, columns: ['T'], rows: [['600123456']], rowIds: [0], delimiter: ',', encoding: 'utf-8',
    }
    const [result] = runProfile(dataset, {
      format: 'datacleanr-profile', version: 1, name: 'x',
      steps: [{ type: 'phone', column: 'T', defaultCountry: 'ES', format: 'E164' }],
    })
    expect(result).toMatchObject({ status: 'skipped', reason: 'unavailable' })
  })
})

describe('parseProfile', () => {
  it.each(cases.invalid)('rejects $description', ({ input, reason }) => {
    let error: unknown = null
    try {
      parseProfile(input)
    } catch (caught) {
      error = caught
    }
    expect(error).toBeInstanceOf(ProfileError)
    expect((error as ProfileError).reason).toBe(reason)
  })

  it('round-trips through serializeProfile', () => {
    const profile = parseProfile(JSON.stringify(cases.run[0].profile))
    expect(parseProfile(serializeProfile(profile))).toEqual(profile)
  })
})
