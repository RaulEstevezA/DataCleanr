import { useI18n } from '../i18n/useI18n.ts'
import { LanguageSwitcher } from './LanguageSwitcher.tsx'
import './AppHeader.css'

export function AppHeader() {
  const { t } = useI18n()

  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__name">DataCleanr</span>
        <span className="app-header__tagline">{t.tagline}</span>
      </div>
      <div className="app-header__actions">
        <p className="app-header__privacy" role="note">
          {t.privacyNotice}
        </p>
        <LanguageSwitcher />
      </div>
    </header>
  )
}
