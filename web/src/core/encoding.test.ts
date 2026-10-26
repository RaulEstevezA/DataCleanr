import { expect, it } from 'vitest'
import cases from '../../../shared/test-cases/encoding.json'
import { decodeText } from './encoding.ts'

const fromHex = (hex: string) => new Uint8Array(hex.split(' ').map((byte) => parseInt(byte, 16)))

it.each(cases)('$description', ({ bytes, expectedText, expectedEncoding }) => {
  expect(decodeText(fromHex(bytes))).toEqual({ text: expectedText, encoding: expectedEncoding })
})
