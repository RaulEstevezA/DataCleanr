import type { ReactNode } from 'react'
import { useI18n } from '../i18n/useI18n.ts'
import './IntroPanel.css'

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
        <a className="button" href="https://github.com/RaulEstevezA/DataCleanr" target="_blank" rel="noopener">
          {t.introCode}
        </a>
      </div>
    </section>
  )
}
