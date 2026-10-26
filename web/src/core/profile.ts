import type { AmountFormat, DecimalSeparator } from './amount.ts'
import { createAmountTransform } from './amount.ts'
import { applyColumnChanges, previewColumnChanges } from './changes.ts'
import { removeRows, type Dataset } from './dataset.ts'
import type { DateFormat, DateInputOrder } from './date.ts'
import { createDateTransform } from './date.ts'
import { findDuplicateRows, mergeRows } from './duplicates.ts'
import type { PhoneFormat, PhoneOptions } from './phone.ts'
import { createReplaceTransform } from './replace.ts'
import { transformIds, transforms, type TransformId } from './transforms.ts'

/**
 * A cleaning profile: replayable steps saved as JSON. The same format is read by the
 * desktop version. Columns are referenced by name so profiles survive reordered columns.
 */
export interface Profile {
  format: 'datacleanr-profile'
  version: 1
  name: string
  steps: ProfileStep[]
}

export type ProfileStep =
  | { type: 'transform'; column: string; transform: TransformId }
  | { type: 'replace'; column: string; find: string; replacement: string; wholeCell: boolean; ignoreCase: boolean }
  | { type: 'phone'; column: string; defaultCountry: string; format: PhoneFormat }
  | { type: 'date'; column: string; inputOrder: DateInputOrder; format: DateFormat; twoDigitYearLimit: number }
  | { type: 'amount'; column: string; ambiguousDecimal: DecimalSeparator; format: AmountFormat; twoDecimals: boolean }
  /** Exact value replacements, e.g. the result of unifying similar values. */
  | { type: 'map'; column: string; mapping: { from: string; to: string }[] }
  /** Exact duplicates only: the first row of each group is kept. */
  | { type: 'removeDuplicates'; columns: string[]; ignoreCaseAndSpaces: boolean; merge: boolean }

export const PROFILE_FORMAT = 'datacleanr-profile'
export const PROFILE_VERSION = 1

export class ProfileError extends Error {
  readonly reason: 'invalid' | 'version' | 'step'
  /** Index of the offending step, for reason "step". */
  readonly step: number | null

  constructor(reason: ProfileError['reason'], step: number | null = null) {
    super(step === null ? reason : `${reason} ${step}`)
    this.reason = reason
    this.step = step
  }
}

type Json = Record<string, unknown>

const isString = (value: unknown): value is string => typeof value === 'string'
const isBoolean = (value: unknown): value is boolean => typeof value === 'boolean'
const oneOf =
  <T extends string>(...options: T[]) =>
  (value: unknown): value is T =>
    options.includes(value as T)

/** Required fields (besides "type") and how to check them, per step type. */
const STEP_FIELDS: Record<ProfileStep['type'], Record<string, (value: unknown) => boolean>> = {
  transform: { column: isString, transform: oneOf(...transformIds) },
  replace: { column: isString, find: isString, replacement: isString, wholeCell: isBoolean, ignoreCase: isBoolean },
  phone: { column: isString, defaultCountry: (v) => isString(v) && /^[A-Z]{2}$/.test(v), format: oneOf('E164', 'INTERNATIONAL', 'NATIONAL') },
  date: {
    column: isString,
    inputOrder: oneOf('DMY', 'MDY'),
    format: oneOf('ISO', 'DMY', 'MDY'),
    twoDigitYearLimit: (v) => Number.isInteger(v) && (v as number) >= 0 && (v as number) <= 99,
  },
  amount: {
    column: isString,
    ambiguousDecimal: oneOf(',', '.'),
    format: oneOf('DOT', 'COMMA', 'DOT_GROUPED', 'COMMA_GROUPED'),
    twoDecimals: isBoolean,
  },
  map: {
    column: isString,
    mapping: (v) => Array.isArray(v) && v.every((m: Json) => isString(m?.from) && isString(m?.to)),
  },
  removeDuplicates: {
    columns: (v) => Array.isArray(v) && v.length > 0 && v.every(isString),
    ignoreCaseAndSpaces: isBoolean,
    merge: isBoolean,
  },
}

function validateStep(step: unknown, index: number): ProfileStep {
  const fields = STEP_FIELDS[(step as Json)?.type as ProfileStep['type']]
  if (!fields) throw new ProfileError('step', index)
  for (const [name, check] of Object.entries(fields)) {
    if (!check((step as Json)[name])) throw new ProfileError('step', index)
  }
  return step as ProfileStep
}

/** Parses and validates a profile file. Unknown extra fields are ignored. */
export function parseProfile(text: string): Profile {
  let data: Json
  try {
    data = JSON.parse(text.replace(/^﻿/, ''))
  } catch {
    throw new ProfileError('invalid')
  }
  if (data?.format !== PROFILE_FORMAT || !Array.isArray(data.steps) || !isString(data.name)) {
    throw new ProfileError('invalid')
  }
  if (data.version !== PROFILE_VERSION) throw new ProfileError('version')
  return { format: PROFILE_FORMAT, version: PROFILE_VERSION, name: data.name, steps: data.steps.map(validateStep) }
}

export function serializeProfile(profile: Profile): string {
  return `${JSON.stringify(profile, null, 2)}\n`
}

export interface StepResult {
  step: ProfileStep
  status: 'applied' | 'skipped'
  reason?: 'missingColumn' | 'unavailable'
  /** Cells changed, or rows removed for removeDuplicates. */
  count: number
  /** Empty cells filled when merging duplicates. */
  filled?: number
  /** Dataset after this step (the same object when nothing changed). */
  dataset: Dataset
}

export interface ProfileDependencies {
  /** Phone support is loaded on demand in the browser; steps are skipped without it. */
  createPhoneTransform?: (options: PhoneOptions) => (value: string) => string
}

function cellTransform(step: Exclude<ProfileStep, { type: 'removeDuplicates' }>, deps: ProfileDependencies) {
  switch (step.type) {
    case 'transform':
      return transforms[step.transform]
    case 'replace':
      return createReplaceTransform(step)
    case 'phone':
      return deps.createPhoneTransform?.({ defaultCountry: step.defaultCountry as PhoneOptions['defaultCountry'], format: step.format }) ?? null
    case 'date':
      return createDateTransform(step)
    case 'amount':
      return createAmountTransform(step)
    case 'map': {
      const mapping = new Map(step.mapping.map(({ from, to }) => [from, to]))
      return (value: string) => mapping.get(value) ?? value
    }
  }
}

function runStep(dataset: Dataset, step: ProfileStep, deps: ProfileDependencies): StepResult {
  const skipped = (reason: StepResult['reason']): StepResult => ({ step, status: 'skipped', reason, count: 0, dataset })
  // Columns are matched by name; with duplicated names, the first one is used
  const indexOf = (name: string) => dataset.columns.indexOf(name)

  if (step.type === 'removeDuplicates') {
    const columns = step.columns.map(indexOf)
    if (columns.some((c) => c < 0)) return skipped('missingColumn')
    const groups = findDuplicateRows(dataset.rows, { columns, ignoreCaseAndSpaces: step.ignoreCaseAndSpaces })
    const rows = [...dataset.rows]
    const remove = new Set<number>()
    let filled = 0
    for (const group of groups) {
      if (step.merge) {
        const merged = mergeRows(group.map((r) => dataset.rows[r]), 0)
        rows[group[0]] = merged.row
        filled += merged.filled.length
      }
      for (const row of group.slice(1)) remove.add(row)
    }
    return { step, status: 'applied', count: remove.size, filled, dataset: removeRows({ ...dataset, rows }, remove) }
  }

  const column = indexOf(step.column)
  if (column < 0) return skipped('missingColumn')
  const transform = cellTransform(step, deps)
  if (!transform) return skipped('unavailable')
  const changes = previewColumnChanges(dataset, column, transform)
  return { step, status: 'applied', count: changes.length, dataset: applyColumnChanges(dataset, column, changes) }
}

/** Runs every step in order. Each result carries the dataset after that step, for the history. */
export function runProfile(dataset: Dataset, profile: Profile, deps: ProfileDependencies = {}): StepResult[] {
  const results: StepResult[] = []
  let current = dataset
  for (const step of profile.steps) {
    const result = runStep(current, step, deps)
    results.push(result)
    current = result.dataset
  }
  return results
}
