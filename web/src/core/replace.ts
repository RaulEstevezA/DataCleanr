export interface ReplaceOptions {
  find: string
  replacement: string
  /** true: the whole cell must match. false: replace every occurrence inside the text. */
  wholeCell: boolean
  ignoreCase: boolean
}

const escapeRegExp = (text: string) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

/**
 * Builds a transform that replaces a user-typed value, e.g. "Transgrau s.l" -> "TransGrau SL".
 * In whole-cell mode surrounding spaces are ignored, so "  Transgrau s.l " also matches.
 */
export function createReplaceTransform({ find, replacement, wholeCell, ignoreCase }: ReplaceOptions) {
  const target = wholeCell ? find.trim() : find
  if (target === '') return (value: string) => value

  if (wholeCell) {
    const normalize = (text: string) => (ignoreCase ? text.toLowerCase() : text)
    const normalizedTarget = normalize(target)
    return (value: string) => (normalize(value.trim()) === normalizedTarget ? replacement : value)
  }

  const pattern = new RegExp(escapeRegExp(target), ignoreCase ? 'gi' : 'g')
  // Function replacer so "$" in the replacement is inserted literally
  return (value: string) => value.replace(pattern, () => replacement)
}
