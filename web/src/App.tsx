import './App.css'
import { AppFooter } from './components/AppFooter.tsx'
import { AppHeader } from './components/AppHeader.tsx'
import { useI18n } from './i18n/useI18n.ts'

function App() {
  const { t } = useI18n()

  return (
    <div className="app">
      <AppHeader />
      <main className="app__main">
        <section className="panel panel--empty">
          <h1>{t.emptyTitle}</h1>
          <p>{t.emptyDescription}</p>
        </section>
      </main>
      <AppFooter />
    </div>
  )
}

export default App
