import type { Dataset } from './dataset.ts'
import { decodeText, type TextEncodingName } from './encoding.ts'

export class XmlImportError extends Error {
  readonly reason: 'invalid' | 'unsupported'

  constructor(reason: XmlImportError['reason']) {
    super(reason)
    this.reason = reason
  }
}

const childElements = (element: Element) => [...element.children]

const XMLNS = 'http://www.w3.org/2000/xmlns/'

/** Real attributes only: namespace declarations (xmlns, xmlns:fe) are not data. */
const dataAttributes = (element: Element) => [...element.attributes].filter((attribute) => attribute.namespaceURI !== XMLNS)

/** Has structure (child elements or attributes), so it can be a row with several columns. */
const isStructured = (element: Element) => element.children.length > 0 || dataAttributes(element).length > 0

/**
 * Finds the elements that represent the rows: the most repeated element name under
 * a single parent. Ties go to the shallowest parent, then to document order.
 * Structured elements are preferred; plain value lists are the fallback.
 */
function findRecords(root: Element): Element[] {
  for (const onlyStructured of [true, false]) {
    let best: Element[] = []
    // Breadth-first, so on equal counts the shallowest (then first) candidate is kept
    const queue: Element[] = [root]
    while (queue.length > 0) {
      const element = queue.shift()!
      const byName = new Map<string, Element[]>()
      for (const child of childElements(element)) {
        queue.push(child)
        if (onlyStructured && !isStructured(child)) continue
        const list = byName.get(child.localName) ?? []
        list.push(child)
        byName.set(child.localName, list)
      }
      for (const records of byName.values()) {
        if (records.length > best.length) best = records
      }
    }
    if (best.length > 0) return best
  }
  return []
}

/**
 * Turns a row element into column -> value. Attributes use "@name", nested elements
 * "parent.child", and repeated children are numbered: "telefono", "telefono[2]".
 */
function flatten(element: Element, prefix: string, into: Map<string, string>) {
  for (const attribute of dataAttributes(element)) into.set(`${prefix}@${attribute.localName}`, attribute.value)
  const seen = new Map<string, number>()
  for (const child of childElements(element)) {
    const count = (seen.get(child.localName) ?? 0) + 1
    seen.set(child.localName, count)
    const path = prefix + (count === 1 ? child.localName : `${child.localName}[${count}]`)
    if (child.children.length > 0) {
      flatten(child, `${path}.`, into)
    } else {
      into.set(path, child.textContent ?? '')
      if (dataAttributes(child).length > 0) flatten(child, `${path}.`, into)
    }
  }
}

function recordToCells(record: Element): Map<string, string> {
  const cells = new Map<string, string>()
  // A plain value (<item>a</item>) is a one-column row named after the element
  if (!isStructured(record)) cells.set(record.localName, record.textContent ?? '')
  else flatten(record, '', cells)
  return cells
}

/**
 * Parses XML that represents a table. Uses the browser's own parser (no external entities are
 * loaded), and rejects entity declarations altogether, the basis of "XML bomb" attacks.
 */
export function parseXmlText(text: string, fileName: string, encoding: TextEncodingName = 'utf-8'): Dataset {
  if (/<!ENTITY/i.test(text)) throw new XmlImportError('invalid')
  const document = new DOMParser().parseFromString(text.replace(/^﻿/, ''), 'application/xml')
  if (document.getElementsByTagName('parsererror').length > 0) throw new XmlImportError('invalid')

  const records = findRecords(document.documentElement)
  if (records.length === 0) throw new XmlImportError('unsupported')

  const cellsPerRecord = records.map(recordToCells)
  const names = new Set<string>()
  for (const cells of cellsPerRecord) for (const name of cells.keys()) names.add(name)
  const columns = [...names]
  const rows = cellsPerRecord.map((cells) => columns.map((name) => cells.get(name) ?? ''))

  return {
    fileName,
    format: 'xml',
    sheet: null,
    columns,
    rows,
    rowIds: rows.map((_, i) => i),
    delimiter: ',',
    encoding,
  }
}

/** Reads and parses an XML file entirely in the browser. */
export async function parseXmlFile(file: File): Promise<Dataset> {
  const { text, encoding } = decodeText(new Uint8Array(await file.arrayBuffer()))
  return parseXmlText(text, file.name, encoding)
}
