import './AppHeader.css'

export function AppHeader() {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__name">DataCleanr</span>
        <span className="app-header__tagline">Clean, normalize and unify tabular data</span>
      </div>
      <p className="app-header__privacy" role="note">
        Processed locally. Your files are never sent to a server.
      </p>
    </header>
  )
}
