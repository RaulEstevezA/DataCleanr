import type { Dataset } from './dataset.ts'
import { decodeText, type TextEncodingName } from './encoding.ts'

export class JsonImportError extends Error {
  readonly reason: 'invalid' | 'unsupported' | 'empty'

  constructor(reason: JsonImportError['reason']) {
    super(reason)
    this.reason = reason
  }
}

/** A JSON number kept exactly as written, so big integers and "1.50" are not altered. */
class RawNumber {
  readonly source: string

  constructor(source: string) {
    this.source = source
  }
}

type JsonValue = string | boolean | null | RawNumber | JsonValue[] | { [key: string]: JsonValue }

function parseKeepingNumbers(text: string): JsonValue {
  // The reviver's third argument (source text) exists in modern browsers; fall back to the parsed number
  return JSON.parse(text, (_key, value, context?: { source?: string }) =>
    typeof value === 'number' ? new RawNumber(context?.source ?? String(value)) : value,
  )
}

const isObject = (value: JsonValue): value is { [key: string]: JsonValue } =>
  typeof value === 'object' && value !== null && !Array.isArray(value) && !(value instanceof RawNumber)

/** Compact JSON text for arrays inside a cell, writing numbers as they were in the file. */
function toJsonText(value: JsonValue): string {
  if (value instanceof RawNumber) return value.source
  if (Array.isArray(value)) return `[${value.map(toJsonText).join(',')}]`
  if (isObject(value)) return `{${Object.entries(value).map(([k, v]) => `${JSON.stringify(k)}:${toJsonText(v)}`).join(',')}}`
  return JSON.stringify(value)
}

function toCellText(value: JsonValue): string {
  if (value === null) return ''
  if (typeof value === 'boolean') return value ? 'TRUE' : 'FALSE'
  if (value instanceof RawNumber) return value.source
  if (typeof value === 'string') return value
  return toJsonText(value)
}

/** {"a": {"b": 1}} -> {"a.b": 1}. Arrays are not flattened: they stay as JSON text in one cell. */
function flatten(object: { [key: string]: JsonValue }, prefix = '', into: Map<string, JsonValue> = new Map()) {
  for (const [key, value] of Object.entries(object)) {
    const name = prefix ? `${prefix}.${key}` : key
    if (isObject(value)) flatten(value, name, into)
    else into.set(name, value)
  }
  return into
}

/**
 * Parses JSON that represents a table: a list of objects, a list of lists (first one
 * is the header), or an object holding a single such list. Values become text.
 */
export function parseJsonText(text: string, fileName: string, encoding: TextEncodingName = 'utf-8'): Dataset {
  let root: JsonValue
  try {
    root = parseKeepingNumbers(text.replace(/^﻿/, ''))
  } catch {
    throw new JsonImportError('invalid')
  }

  if (isObject(root)) {
    const lists = Object.values(root).filter(Array.isArray)
    if (lists.length !== 1 || Object.keys(root).length !== 1) throw new JsonImportError('unsupported')
    root = lists[0]
  }
  if (!Array.isArray(root)) throw new JsonImportError('unsupported')
  if (root.length === 0) throw new JsonImportError('empty')

  let columns: string[]
  let rows: string[][]
  if (root.every(isObject)) {
    const flattened = root.map((object) => flatten(object))
    const names = new Set<string>()
    for (const row of flattened) for (const name of row.keys()) names.add(name)
    columns = [...names]
    rows = flattened.map((row) => columns.map((name) => (row.has(name) ? toCellText(row.get(name)!) : '')))
  } else if (root.every(Array.isArray)) {
    const [header, ...body] = root as JsonValue[][]
    columns = header.map(toCellText)
    rows = body.map((row) => columns.map((_, i) => (i < row.length ? toCellText(row[i]) : '')))
  } else {
    throw new JsonImportError('unsupported')
  }

  return {
    fileName,
    format: 'json',
    sheet: null,
    columns,
    rows,
    rowIds: rows.map((_, i) => i),
    delimiter: ',',
    encoding,
  }
}

/** Reads and parses a JSON file entirely in the browser. */
export async function parseJsonFile(file: File): Promise<Dataset> {
  const { text, encoding } = decodeText(new Uint8Array(await file.arrayBuffer()))
  return parseJsonText(text, file.name, encoding)
}
