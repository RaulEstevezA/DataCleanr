import type { ReactNode } from 'react'
import { useI18n } from '../i18n/useI18n.ts'
import './IntroPanel.css'

const TOOLS_URL = 'https://raulesteveza.github.io/tools/'
const SOURCE_URL = 'https://github.com/RaulEstevezA/DataCleanr'
// Installers will be published as GitHub Releases; until then the button is shown disabled
const DESKTOP_DOWNLOAD_URL: string | null = null

/** Presentation card shown before a file is loaded, styled like the portfolio's project windows. */
export function IntroPanel({ children }: { children: ReactNode }) {
  const { t } = useI18n()

  return (
    <section className="intro window">
      <div className="intro__text">
        <h1>DataCleanr</h1>
        <p className="intro__subtitle">{t.tagline}</p>
        <p className="intro__description">{t.introDescription}</p>
      </div>

      <div className="intro__callout" role="note">
        <p className="intro__callout-title">{t.introPrivacyTitle}</p>
        <ul>
          {t.introPrivacyPoints.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
      </div>

      {children}

      <div className="intro__actions">
        {DESKTOP_DOWNLOAD_URL ? (
          <a className="button" href={DESKTOP_DOWNLOAD_URL} target="_blank" rel="noopener">
            {t.introDownload}
          </a>
        ) : (
          <button type="button" className="button" disabled title={t.introDownloadSoon}>
            {t.introDownload} ({t.introSoon})
          </button>
        )}
        <a className="button" href={SOURCE_URL} target="_blank" rel="noopener">
          {t.introCode}
        </a>
        <a className="button" href={TOOLS_URL}>
          {t.introAllTools}
        </a>
      </div>
    </section>
  )
}
