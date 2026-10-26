export type TextEncodingName = 'utf-8' | 'utf-16le' | 'utf-16be' | 'windows-1252'

/**
 * Decodes file bytes guessing the encoding, so accents and "ñ" display correctly:
 * 1. A UTF-16 byte order mark wins.
 * 2. Otherwise, if the bytes are valid UTF-8 they are UTF-8 (BOM removed).
 * 3. Otherwise they are Windows-1252, what Excel uses for "CSV" on Spanish/Western Windows.
 */
export function decodeText(bytes: Uint8Array): { text: string; encoding: TextEncodingName } {
  if (bytes[0] === 0xff && bytes[1] === 0xfe) return decodeAs(bytes, 'utf-16le')
  if (bytes[0] === 0xfe && bytes[1] === 0xff) return decodeAs(bytes, 'utf-16be')
  try {
    return { text: new TextDecoder('utf-8', { fatal: true }).decode(bytes), encoding: 'utf-8' }
  } catch {
    return decodeAs(bytes, 'windows-1252')
  }
}

function decodeAs(bytes: Uint8Array, encoding: TextEncodingName) {
  return { text: new TextDecoder(encoding).decode(bytes), encoding }
}
