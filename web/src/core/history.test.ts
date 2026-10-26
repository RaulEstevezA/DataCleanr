import { describe, expect, it } from 'vitest'
import { canRedo, canUndo, createHistory, currentEntry, goTo, pushEntry, redo, undo } from './history.ts'

describe('history', () => {
  const abc = pushEntry(pushEntry(createHistory('a'), 'b'), 'c')

  it('starts with a single entry and nothing to undo or redo', () => {
    const history = createHistory('a')
    expect(currentEntry(history)).toBe('a')
    expect(canUndo(history)).toBe(false)
    expect(canRedo(history)).toBe(false)
  })

  it('undoes and redoes', () => {
    const back = undo(abc)
    expect(currentEntry(back)).toBe('b')
    expect(canRedo(back)).toBe(true)
    expect(currentEntry(redo(back))).toBe('c')
  })

  it('does not go past the ends', () => {
    expect(currentEntry(redo(abc))).toBe('c')
    expect(currentEntry(undo(undo(undo(abc))))).toBe('a')
  })

  it('discards redoable entries when a new one is pushed', () => {
    const branched = pushEntry(undo(undo(abc)), 'x')
    expect(branched.entries).toEqual(['a', 'x'])
    expect(canRedo(branched)).toBe(false)
  })

  it('jumps to any entry', () => {
    expect(currentEntry(goTo(abc, 0))).toBe('a')
    expect(currentEntry(goTo(abc, 99))).toBe('c')
  })

  it('never mutates the previous history', () => {
    const snapshot = structuredClone(abc)
    pushEntry(undo(abc), 'x')
    expect(abc).toEqual(snapshot)
  })
})
