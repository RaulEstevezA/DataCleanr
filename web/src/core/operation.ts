import type { TransformId } from './transforms.ts'

/** Everything that can be applied to the cells of one column. */
export type CellAction = TransformId | 'custom' | 'phone' | 'date' | 'amount' | 'similar'

/**
 * What a history step did, stored as data (not as translated text) so it can be
 * displayed in any language and, later, replayed as a cleaning profile.
 */
export type Operation =
  | { kind: 'import' }
  | { kind: 'cells'; column: number; action: CellAction; count: number }
  | { kind: 'removeRows'; mode: 'exact' | 'similar'; count: number }
