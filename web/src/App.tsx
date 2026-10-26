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
import { EmptySheetError, sheetToDataset, type XlsxSheet } from './core/xlsx.ts'
import { downloadTextFile } from './utils/download.ts'
import { readWorkbook } from './utils/readWorkbook.ts'

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
  // All sheets of the imported Excel file, to switch between them; null for CSV
  const [sheets, setSheets] = useState<XlsxSheet[] | null>(null)

  const dataset = history ? currentEntry(history).dataset : null
  const original = history ? history.entries[0].dataset : null

  function startWith(loaded: Dataset) {
    setHistory(createHistory<HistoryStep>({ dataset: loaded, operation: { kind: 'import' } }))
    setSelectedColumn(null)
    setShowDuplicates(false)
    setNotice(null)
  }

  async function handleFile(file: File) {
    const name = file.name.toLowerCase()
    if (name.endsWith('.xls')) {
      setError(t.errorOldExcel)
      return
    }
    if (!name.endsWith('.csv') && !name.endsWith('.xlsx')) {
      setError(t.errorUnsupported)
      return
    }
    setLoading(true)
    setError(null)
    try {
      if (name.endsWith('.csv')) {
        setSheets(null)
        startWith(await parseCsvFile(file))
      } else {
        const workbook = await readWorkbook(file)
        // Open the first sheet that has data
        const first = workbook.find((sheet) => sheet.data.some((row) => row.some((cell) => cell !== null)))
        if (!first) throw new EmptySheetError(file.name)
        setSheets(workbook)
        startWith(sheetToDataset(first, file.name))
      }
    } catch {
      setError(name.endsWith('.csv') ? t.errorParse : t.errorParseExcel)
    } finally {
      setLoading(false)
    }
  }

  function selectSheet(name: string) {
    const sheet = sheets?.find(({ sheet }) => sheet === name)
    if (!sheet || !dataset) return
    if (hasChanges && !window.confirm(t.confirmDiscardSheet)) return
    try {
      startWith(sheetToDataset(sheet, dataset.fileName))
    } catch {
      setNotice(() => (m: Messages) => m.emptySheet(name))
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
    setSheets(null)
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
              sheets={sheets?.map(({ sheet }) => sheet) ?? null}
              onSelectSheet={selectSheet}
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
