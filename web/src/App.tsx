import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'
import { AppFooter } from './components/AppFooter.tsx'
import { AppHeader } from './components/AppHeader.tsx'
import { DataTable } from './components/DataTable.tsx'
import { DatasetSummary } from './components/DatasetSummary.tsx'
import { DuplicatesPanel } from './components/DuplicatesPanel.tsx'
import { ExportPanel } from './components/ExportPanel.tsx'
import { ProfilePanel } from './components/ProfilePanel.tsx'
import { FileImport } from './components/FileImport.tsx'
import { IntroPanel } from './components/IntroPanel.tsx'
import { HistoryPanel, type HistoryStep } from './components/HistoryPanel.tsx'
import { TransformPanel } from './components/TransformPanel.tsx'
import type { Messages } from './i18n/messages.ts'
import { useI18n } from './i18n/useI18n.ts'
import { parseCsvFile } from './core/csv.ts'
import { JsonImportError, parseJsonFile } from './core/json.ts'
import { parseXmlFile, XmlImportError } from './core/xml.ts'
import { columnLabel, countModifiedCells, type Dataset } from './core/dataset.ts'
import { canRedo, canUndo, createHistory, currentEntry, goTo, pushEntry, redo, undo, type History } from './core/history.ts'
import type { CellAction, Operation } from './core/operation.ts'
import { parseProfile, ProfileError, runProfile, type ProfileStep, type Profile, type StepResult } from './core/profile.ts'
import { EmptySheetError, sheetToDataset, type XlsxSheet } from './core/xlsx.ts'
import { readWorkbook } from './utils/readWorkbook.ts'

function App() {
  const { t } = useI18n()
  // Every applied operation adds a new dataset version; the first entry is the untouched original
  const [history, setHistory] = useState<History<HistoryStep> | null>(null)
  const [selectedColumn, setSelectedColumn] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // Stored as a function of the messages so it follows language changes
  const [notice, setNotice] = useState<{ text: (t: Messages) => string; tone: 'success' | 'warning' } | null>(null)
  const showNotice = (text: (t: Messages) => string, tone: 'success' | 'warning' = 'success') => setNotice({ text, tone })
  // Dataset-level panels; only one is open at a time, and never together with a column panel
  const [panel, setPanel] = useState<'duplicates' | 'export' | 'profile' | null>(null)
  // A loaded profile and its dry run, computed from the history entry it was loaded on
  const [profileRun, setProfileRun] = useState<{ profile: Profile; results: StepResult[]; baseIndex: number } | null>(null)
  // All sheets of the imported Excel file, to switch between them; null for CSV
  const [sheets, setSheets] = useState<XlsxSheet[] | null>(null)

  const dataset = history ? currentEntry(history).dataset : null
  const original = history ? history.entries[0].dataset : null

  function startWith(loaded: Dataset) {
    setHistory(createHistory<HistoryStep>({ dataset: loaded, operation: { kind: 'import' }, profileStep: null }))
    setSelectedColumn(null)
    setPanel(null)
    setNotice(null)
  }

  async function handleFile(file: File) {
    const name = file.name.toLowerCase()
    if (name.endsWith('.xls')) {
      setError(t.errorOldExcel)
      return
    }
    if (!['.csv', '.xlsx', '.json', '.xml'].some((extension) => name.endsWith(extension))) {
      setError(t.errorUnsupported)
      return
    }
    setLoading(true)
    setError(null)
    try {
      if (name.endsWith('.csv')) {
        setSheets(null)
        startWith(await parseCsvFile(file))
      } else if (name.endsWith('.json')) {
        setSheets(null)
        startWith(await parseJsonFile(file))
      } else if (name.endsWith('.xml')) {
        setSheets(null)
        startWith(await parseXmlFile(file))
      } else {
        const workbook = await readWorkbook(file)
        // Open the first sheet that has data
        const first = workbook.find((sheet) => sheet.data.some((row) => row.some((cell) => cell !== null)))
        if (!first) throw new EmptySheetError(file.name)
        setSheets(workbook)
        startWith(sheetToDataset(first, file.name))
      }
    } catch (error) {
      if (error instanceof JsonImportError) setError(t.errorParseJson[error.reason])
      else if (error instanceof XmlImportError) setError(t.errorParseXml[error.reason])
      else setError(name.endsWith('.csv') ? t.errorParse : t.errorParseExcel)
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
      showNotice((m) => m.emptySheet(name), 'warning')
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
    setPanel(null)
    setNotice(null)
  }

  function openDuplicates() {
    setPanel('duplicates')
    setSelectedColumn(null)
    setNotice(null)
  }

  function handleRemoveRows(
    updated: Dataset,
    removedCount: number,
    mode: 'exact' | 'similar',
    filled: number,
    profileStep: ProfileStep | null,
  ) {
    addStep({ dataset: updated, operation: { kind: 'removeRows', mode, count: removedCount, filled }, profileStep })
    setPanel(null)
    showNotice((m) => m.rowsRemoved(removedCount, filled))
  }

  function handleApply(updated: Dataset, appliedCount: number, action: CellAction, profileStep: ProfileStep) {
    if (selectedColumn === null) return
    addStep({
      dataset: updated,
      operation: { kind: 'cells', column: selectedColumn, action, count: appliedCount },
      profileStep,
    })
    const column = columnLabel(updated, selectedColumn)
    showNotice((m) => m.changesApplied(appliedCount, column))
  }

  async function loadProfile(file: File) {
    if (!history || !dataset) return
    try {
      const profile = parseProfile(await file.text())
      // Phone rules are large: load them only if the profile needs them
      const needsPhone = profile.steps.some((step) => step.type === 'phone')
      const phone = needsPhone ? await import('./core/phone.ts') : null
      const results = runProfile(dataset, profile, { createPhoneTransform: phone?.createPhoneTransform })
      setProfileRun({ profile, results, baseIndex: history.index })
      setPanel('profile')
      setSelectedColumn(null)
      setNotice(null)
    } catch (error) {
      const reason = error instanceof ProfileError ? error.reason : 'invalid'
      const step = error instanceof ProfileError ? error.step : null
      showNotice((m) => m.profileError[reason](step === null ? 0 : step + 1), 'warning')
    }
  }

  function applyProfile() {
    if (!history || !profileRun) return
    let next = history
    for (const result of profileRun.results) {
      if (result.status !== 'applied' || result.count === 0) continue
      const { step } = result
      const operation: Operation =
        step.type === 'removeDuplicates'
          ? { kind: 'removeRows', mode: 'exact', count: result.count, filled: result.filled ?? 0 }
          : {
              kind: 'cells',
              column: result.dataset.columns.indexOf(step.column),
              action: step.type === 'transform' ? step.transform : step.type === 'replace' ? 'custom' : step.type === 'map' ? 'similar' : step.type,
              count: result.count,
            }
      next = pushEntry(next, { dataset: result.dataset, operation, profileStep: step })
    }
    const applied = next.index - history.index
    const name = profileRun.profile.name
    setHistory(next)
    setPanel(null)
    setProfileRun(null)
    showNotice((m) => m.profileApplied(name, applied))
  }

  function openExport() {
    setPanel('export')
    setSelectedColumn(null)
    setNotice(null)
  }

  function handleReset() {
    if (hasChanges && !window.confirm(t.confirmDiscard)) return
    setHistory(null)
    setSheets(null)
    setSelectedColumn(null)
    setPanel(null)
    setNotice(null)
  }

  return (
    <div className="app">
      <AppHeader wide={dataset !== null} />
      <main className={`app__main${dataset ? ' app__main--wide' : ''}`}>
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
              onExport={openExport}
              onLoadProfile={loadProfile}
              onReset={handleReset}
            />
            <HistoryPanel history={history} onGoTo={(index) => moveInHistory((h) => goTo(h, index))} />
            {panel === 'profile' && profileRun && profileRun.baseIndex === history.index && (
              <ProfilePanel
                profile={profileRun.profile}
                results={profileRun.results}
                onApply={applyProfile}
                onClose={() => setPanel(null)}
              />
            )}
            {panel === 'export' && <ExportPanel key={history.index} dataset={dataset} onClose={() => setPanel(null)} />}
            {panel === 'duplicates' && (
              <DuplicatesPanel
                key={history.index}
                dataset={dataset}
                onRemove={handleRemoveRows}
                onClose={() => setPanel(null)}
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
              <p className={`app__notice app__notice--${notice.tone}`} role="status">
                {notice.text(t)}
              </p>
            )}
            <DataTable
              dataset={dataset}
              selectedColumn={selectedColumn}
              onSelectColumn={selectColumn}
            />
          </div>
        ) : (
          <IntroPanel>
            <FileImport onFile={handleFile} loading={loading} error={error} />
          </IntroPanel>
        )}
      </main>
      <AppFooter />
    </div>
  )
}

export default App
