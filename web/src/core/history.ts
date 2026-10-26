/**
 * Linear undo/redo history. Immutable: every function returns a new history.
 * `index` points at the current entry; entries after it can be redone.
 */
export interface History<T> {
  entries: T[]
  index: number
}

export function createHistory<T>(first: T): History<T> {
  return { entries: [first], index: 0 }
}

export function currentEntry<T>(history: History<T>): T {
  return history.entries[history.index]
}

/** Adds an entry after the current one. Anything that could be redone is discarded. */
export function pushEntry<T>(history: History<T>, entry: T): History<T> {
  return { entries: [...history.entries.slice(0, history.index + 1), entry], index: history.index + 1 }
}

export function goTo<T>(history: History<T>, index: number): History<T> {
  return { ...history, index: Math.min(Math.max(index, 0), history.entries.length - 1) }
}

export const canUndo = (history: History<unknown>) => history.index > 0
export const canRedo = (history: History<unknown>) => history.index < history.entries.length - 1
export const undo = <T>(history: History<T>) => goTo(history, history.index - 1)
export const redo = <T>(history: History<T>) => goTo(history, history.index + 1)
