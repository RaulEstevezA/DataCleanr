import './App.css'
import { AppFooter } from './components/AppFooter.tsx'
import { AppHeader } from './components/AppHeader.tsx'

function App() {
  return (
    <div className="app">
      <AppHeader />
      <main className="app__main">
        <section className="panel panel--empty">
          <h1>Import a file to get started</h1>
          <p>Load a CSV file to preview its data, pick a column and clean it.</p>
        </section>
      </main>
      <AppFooter />
    </div>
  )
}

export default App
