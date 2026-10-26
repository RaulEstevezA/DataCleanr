import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'
import { AppFooter } from './components/AppFooter.tsx'
import { AppHeader } from './components/AppHeader.tsx'
import { DataTable } from './components/DataTable.tsx'
import { DatasetSummary } from './components/DatasetSummary.tsx'
import { DuplicatesPanel } from './components/DuplicatesPanel.tsx'
import { FileImport } from './components/FileImport.tsx'
import { HistoryPanel, type HistoryStep } from './components/HistoryPanel.tsx'
import { TransformPanel } from './components/TransformPanel.tsx'
import type { Messages } from './i18n/messages.ts'
import { useI18n } from './i18n/useI18n.ts'
import { cleanFileName, parseCsvFile, serializeCsv } from './core/csv.ts'
import { columnLabel, countModifiedCells, type Dataset } from './core/dataset.ts'
import { canRedo, canUndo, createHistory, currentEntry, goTo, pushEntry, redo, undo, type History } from './core/history.ts'
import type { CellAction } from './core/operation.ts'
import { downloadTextFile } from './utils/download.ts'

function App() {
  const { t } = useI18n()
  // Every applied operation adds a new dataset version; the first entry is the untouched original
  const [history, setHistory] = useState<History<HistoryStep> | null>(null)
  const [selectedColumn, setSelectedColumn] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // Stored as a function of the messages so it follows language changes
  const [notice, setNotice] = useState<((t: Messages) => string) | null>(null)
  const [showDuplicates, setShowDuplicates] = useState(false)

  const dataset = history ? currentEntry(history).dataset : null
  const original = history ? history.entries[0].dataset : null

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError(t.errorNotCsv)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const loaded = await parseCsvFile(file)
      setHistory(createHistory<HistoryStep>({ dataset: loaded, operation: { kind: 'import' } }))
      setSelectedColumn(null)
      setNotice(null)
    } catch {
      setError(t.errorParse)
    } finally {
      setLoading(false)
    }
  }

  const modifiedCells = useMemo(
    () => (original && dataset ? countModifiedCells(original, dataset) : 0),
    [original, dataset],
  )
  const removedRows = original && dataset ? original.rows.length - dataset.rows.length : 0
  const hasChanges = modifiedCells > 0 || removedRows > 0

  function addStep(step: HistoryStep) {
    if (history) setHistory(pushEntry(history, step))
  }

  const moveInHistory = useCallback((move: (history: History<HistoryStep>) => History<HistoryStep>) => {
    setHistory((current) => (current ? move(current) : current))
    setNotice(null)
  }, [])

  // Cmd/Ctrl+Z to undo, Cmd/Ctrl+Shift+Z or Ctrl+Y to redo (text fields keep their own undo)
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement
      if (target.closest('input, textarea, select, [contenteditable]')) return
      if (!(event.metaKey || event.ctrlKey)) return
      const key = event.key.toLowerCase()
      if (key === 'z' && !event.shiftKey) moveInHistory(undo)
      else if ((key === 'z' && event.shiftKey) || key === 'y') moveInHistory(redo)
      else return
      event.preventDefault()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [moveInHistory])

  function selectColumn(index: number) {
    setSelectedColumn(index)
    setShowDuplicates(false)
    setNotice(null)
  }

  function openDuplicates() {
    setShowDuplicates(true)
    setSelectedColumn(null)
    setNotice(null)
  }

  function handleRemoveRows(updated: Dataset, removedCount: number, mode: 'exact' | 'similar') {
    addStep({ dataset: updated, operation: { kind: 'removeRows', mode, count: removedCount } })
    setShowDuplicates(false)
    setNotice(() => (m: Messages) => m.rowsRemoved(removedCount))
  }

  function handleApply(updated: Dataset, appliedCount: number, action: CellAction) {
    if (selectedColumn === null) return
    addStep({ dataset: updated, operation: { kind: 'cells', column: selectedColumn, action, count: appliedCount } })
    const column = columnLabel(updated, selectedColumn)
    setNotice(() => (m: Messages) => m.changesApplied(appliedCount, column))
  }

  function handleExport() {
    if (!dataset) return
    downloadTextFile(serializeCsv(dataset), cleanFileName(dataset.fileName), 'text/csv;charset=utf-8')
  }

  function handleReset() {
    if (hasChanges && !window.confirm(t.confirmDiscard)) return
    setHistory(null)
    setSelectedColumn(null)
    setShowDuplicates(false)
    setNotice(null)
  }

  return (
    <div className="app">
      <AppHeader />
      <main className="app__main">
        {history && dataset ? (
          <div className="app__workspace">
            <DatasetSummary
              dataset={dataset}
              modifiedCells={modifiedCells}
              removedRows={removedRows}
              selectedColumn={selectedColumn}
              onSelectColumn={selectColumn}
              onFindDuplicates={openDuplicates}
              canUndo={canUndo(history)}
              canRedo={canRedo(history)}
              onUndo={() => moveInHistory(undo)}
              onRedo={() => moveInHistory(redo)}
              onExport={handleExport}
              onReset={handleReset}
            />
            <HistoryPanel history={history} onGoTo={(index) => moveInHistory((h) => goTo(h, index))} />
            {showDuplicates && (
              <DuplicatesPanel
                key={history.index}
                dataset={dataset}
                onRemove={handleRemoveRows}
                onClose={() => setShowDuplicates(false)}
              />
            )}
            {selectedColumn !== null && (
              <TransformPanel
                key={`${selectedColumn}-${history.index}`}
                dataset={dataset}
                column={selectedColumn}
                onApply={handleApply}
              />
            )}
            {notice && (
              <p className="app__notice" role="status">
                {notice(t)}
              </p>
            )}
            <DataTable
              dataset={dataset}
              selectedColumn={selectedColumn}
              onSelectColumn={selectColumn}
            />
          </div>
        ) : (
          <FileImport onFile={handleFile} loading={loading} error={error} />
        )}
      </main>
      <AppFooter />
    </div>
  )
}

export default App
