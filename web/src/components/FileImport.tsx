import { useRef, useState, type DragEvent } from 'react'
import { useI18n } from '../i18n/useI18n.ts'
import './FileImport.css'

interface FileImportProps {
  onFile: (file: File) => void
  loading: boolean
  error: string | null
}

export function FileImport({ onFile, loading, error }: FileImportProps) {
  const { t } = useI18n()
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function handleDrop(event: DragEvent) {
    event.preventDefault()
    setDragging(false)
    const file = event.dataTransfer.files[0]
    if (file) onFile(file)
  }

  return (
    <section
      className={`file-import${dragging ? ' file-import--dragging' : ''}`}
      onDragOver={(event) => {
        event.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <h2>{t.emptyTitle}</h2>
      <p>{t.emptyDescription}</p>
      <button
        type="button"
        className="button button--primary"
        disabled={loading}
        onClick={() => inputRef.current?.click()}
      >
        {loading ? t.importLoading : t.importButton}
      </button>
      <p className="file-import__hint">{t.importHint}</p>
      {error && (
        <p className="file-import__error" role="alert">
          {error}
        </p>
      )}
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.json,.xml,text/csv,application/json,application/xml,text/xml,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        hidden
        onChange={(event) => {
          const file = event.target.files?.[0]
          if (file) onFile(file)
          event.target.value = ''
        }}
      />
    </section>
  )
}
