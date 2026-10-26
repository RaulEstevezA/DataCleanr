import { useMemo, useState } from 'react'
import './App.css'
import { AppFooter } from './components/AppFooter.tsx'
import { AppHeader } from './components/AppHeader.tsx'
import { DataTable } from './components/DataTable.tsx'
import { DatasetSummary } from './components/DatasetSummary.tsx'
import { DuplicatesPanel } from './components/DuplicatesPanel.tsx'
import { FileImport } from './components/FileImport.tsx'
import { TransformPanel } from './components/TransformPanel.tsx'
import { useI18n } from './i18n/useI18n.ts'
import { cleanFileName, parseCsvFile, serializeCsv } from './core/csv.ts'
import { columnLabel, countModifiedCells, type Dataset } from './core/dataset.ts'
import { downloadTextFile } from './utils/download.ts'

function App() {
  const { t } = useI18n()
  // The original is kept untouched until export; edits always produce a new `dataset`
  const [original, setOriginal] = useState<Dataset | null>(null)
  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [selectedColumn, setSelectedColumn] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [showDuplicates, setShowDuplicates] = useState(false)

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError(t.errorNotCsv)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const loaded = await parseCsvFile(file)
      setOriginal(loaded)
      setDataset(loaded)
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

  function handleRemoveRows(updated: Dataset, removedCount: number) {
    setDataset(updated)
    setShowDuplicates(false)
    setNotice(t.rowsRemoved(removedCount))
  }

  function handleApply(updated: Dataset, appliedCount: number) {
    setDataset(updated)
    if (selectedColumn !== null) {
      setNotice(t.changesApplied(appliedCount, columnLabel(updated, selectedColumn)))
    }
  }

  function handleExport() {
    if (!dataset) return
    downloadTextFile(serializeCsv(dataset), cleanFileName(dataset.fileName), 'text/csv;charset=utf-8')
  }

  function handleReset() {
    if (hasChanges && !window.confirm(t.confirmDiscard)) return
    setOriginal(null)
    setDataset(null)
    setSelectedColumn(null)
    setShowDuplicates(false)
    setNotice(null)
  }

  return (
    <div className="app">
      <AppHeader />
      <main className="app__main">
        {dataset ? (
          <div className="app__workspace">
            <DatasetSummary
              dataset={dataset}
              modifiedCells={modifiedCells}
              removedRows={removedRows}
              selectedColumn={selectedColumn}
              onSelectColumn={selectColumn}
              onFindDuplicates={openDuplicates}
              onExport={handleExport}
              onReset={handleReset}
            />
            {showDuplicates && (
              <DuplicatesPanel
                dataset={dataset}
                onRemove={handleRemoveRows}
                onClose={() => setShowDuplicates(false)}
              />
            )}
            {selectedColumn !== null && (
              <TransformPanel
                key={selectedColumn}
                dataset={dataset}
                column={selectedColumn}
                onApply={handleApply}
              />
            )}
            {notice && (
              <p className="app__notice" role="status">
                {notice}
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
