import { useState } from 'react'
import './App.css'
import { AppFooter } from './components/AppFooter.tsx'
import { AppHeader } from './components/AppHeader.tsx'
import { DataTable } from './components/DataTable.tsx'
import { DatasetSummary } from './components/DatasetSummary.tsx'
import { FileImport } from './components/FileImport.tsx'
import { TransformPanel } from './components/TransformPanel.tsx'
import { useI18n } from './i18n/useI18n.ts'
import { parseCsvFile } from './lib/csv.ts'
import type { Dataset } from './lib/dataset.ts'

function App() {
  const { t, language } = useI18n()
  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [selectedColumn, setSelectedColumn] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError(t.errorNotCsv)
      return
    }
    setLoading(true)
    setError(null)
    try {
      setDataset(await parseCsvFile(file))
      setSelectedColumn(null)
      setNotice(null)
    } catch {
      setError(t.errorParse)
    } finally {
      setLoading(false)
    }
  }

  function selectColumn(index: number) {
    setSelectedColumn(index)
    setNotice(null)
  }

  function handleApply(updated: Dataset, appliedCount: number) {
    setDataset(updated)
    if (selectedColumn !== null) {
      setNotice(t.changesApplied(appliedCount.toLocaleString(language), updated.columns[selectedColumn]))
    }
  }

  return (
    <div className="app">
      <AppHeader />
      <main className="app__main">
        {dataset ? (
          <div className="app__workspace">
            <DatasetSummary
              dataset={dataset}
              selectedColumn={selectedColumn}
              onSelectColumn={selectColumn}
              onReset={() => setDataset(null)}
            />
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
