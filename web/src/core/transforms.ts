/**
 * Basic text transformations. Each one is a pure function: it never mutates
 * the dataset, it only computes the proposed value for a single cell.
 */

export type TransformId = 'trim' | 'collapseSpaces' | 'lowercase' | 'uppercase' | 'titleCase'

const trim = (value: string) => value.trim()

/** Replaces any run of whitespace (spaces, tabs, non-breaking spaces) with a single space. */
const collapseSpaces = (value: string) => value.replace(/\s+/g, ' ')

const lowercase = (value: string) => value.toLowerCase()

const uppercase = (value: string) => value.toUpperCase()

/** Capitalizes the first letter of each word, including after hyphens: "jean-luc PÉREZ" -> "Jean-Luc Pérez". */
const titleCase = (value: string) =>
  value.toLowerCase().replace(/(^|[\s-])(\p{L})/gu, (_, separator: string, letter: string) => separator + letter.toUpperCase())

export const transforms: Record<TransformId, (value: string) => string> = {
  trim,
  collapseSpaces,
  lowercase,
  uppercase,
  titleCase,
}

export const transformIds = Object.keys(transforms) as TransformId[]
