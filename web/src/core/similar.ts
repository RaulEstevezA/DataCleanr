export interface SimilarOptions {
  /** Minimum similarity (0-100) for two values to be grouped. Same scale as RapidFuzz `fuzz.ratio`. */
  threshold: number
  /** Ignore trailing legal forms (S.L., S.A., Inc...) when comparing. */
  ignoreLegalForms: boolean
}

export interface Variant {
  value: string
  count: number
}

export interface SimilarGroup {
  /** Most frequent first. */
  variants: Variant[]
  /** Proposed value to unify the group: the most frequent variant. */
  suggested: string
}

const LEGAL_FORMS = new Set([
  'sl', 'sa', 'slu', 'sll', 'slne', 'sau', 'scp', 'cb', 'sc', 'scoop', 'sccl',
  'inc', 'ltd', 'llc', 'plc', 'corp', 'co', 'gmbh', 'ag', 'sas', 'sarl', 'srl', 'spa', 'bv', 'nv',
])

/** Deterministic order shared with the Python version: by code point, not by locale. */
const byCodePoint = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0)

/**
 * Key used to compare values: lowercase, no accents, no punctuation, no spaces.
 * "Trans Grau S.L." -> "transgrausl", or "transgrau" when ignoring legal forms.
 */
export function comparisonKey(value: string, ignoreLegalForms: boolean): string {
  const tokens = value
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .toLowerCase()
    .replace(/\./g, '')
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim()
    .split(' ')
    .filter(Boolean)

  if (ignoreLegalForms) {
    while (tokens.length > 1) {
      const last = tokens[tokens.length - 1]
      if (LEGAL_FORMS.has(last)) {
        tokens.pop()
        continue
      }
      // "S. L." becomes the single-letter tokens "s", "l"
      const lastTwo = tokens.slice(-2).join('')
      if (tokens.length > 2 && last.length === 1 && tokens[tokens.length - 2].length === 1 && LEGAL_FORMS.has(lastTwo)) {
        tokens.splice(-2)
        continue
      }
      break
    }
  }
  return tokens.join('')
}

function longestCommonSubsequence(a: string, b: string): number {
  let previous = new Array<number>(b.length + 1).fill(0)
  for (let i = 1; i <= a.length; i++) {
    const current = new Array<number>(b.length + 1).fill(0)
    for (let j = 1; j <= b.length; j++) {
      current[j] = a[i - 1] === b[j - 1] ? previous[j - 1] + 1 : Math.max(previous[j], current[j - 1])
    }
    previous = current
  }
  return previous[b.length]
}

/** Similarity 0-100, equivalent to RapidFuzz `fuzz.ratio` (normalized Indel similarity). */
export function similarity(a: string, b: string): number {
  if (a.length + b.length === 0) return 100
  return (200 * longestCommonSubsequence(a, b)) / (a.length + b.length)
}

/**
 * Groups values of a column that probably mean the same thing.
 * 1. Values with the same comparison key are always together.
 * 2. Keys are clustered greedily, most frequent first: a key joins the first
 *    cluster whose leader is at least `threshold` similar (no chaining).
 * Only groups with two or more distinct variants are returned.
 */
export function groupSimilarValues(values: string[], { threshold, ignoreLegalForms }: SimilarOptions): SimilarGroup[] {
  const counts = new Map<string, number>()
  for (const value of values) {
    if (value.trim() !== '') counts.set(value, (counts.get(value) ?? 0) + 1)
  }

  const buckets = new Map<string, Variant[]>()
  for (const [value, count] of counts) {
    const key = comparisonKey(value, ignoreLegalForms)
    if (key === '') continue
    const bucket = buckets.get(key) ?? []
    bucket.push({ value, count })
    buckets.set(key, bucket)
  }

  const total = (variants: Variant[]) => variants.reduce((sum, variant) => sum + variant.count, 0)
  const sortedBuckets = [...buckets].sort(([keyA, a], [keyB, b]) => total(b) - total(a) || byCodePoint(keyA, keyB))

  const clusters: { leader: string; variants: Variant[] }[] = []
  for (const [key, variants] of sortedBuckets) {
    const cluster = clusters.find(({ leader }) => similarity(key, leader) >= threshold)
    if (cluster) cluster.variants.push(...variants)
    else clusters.push({ leader: key, variants: [...variants] })
  }

  return clusters
    .filter(({ variants }) => variants.length > 1)
    .sort((a, b) => total(b.variants) - total(a.variants) || byCodePoint(a.leader, b.leader))
    .map(({ variants }) => {
      const sorted = [...variants].sort((a, b) => b.count - a.count || byCodePoint(a.value, b.value))
      return { variants: sorted, suggested: sorted[0].value }
    })
}
