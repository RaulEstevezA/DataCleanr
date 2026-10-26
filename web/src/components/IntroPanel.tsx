import type { ReactNode } from 'react'
import { useI18n } from '../i18n/useI18n.ts'
import { detectPlatform, downloadUrl, RELEASES_URL } from '../utils/desktopDownload.ts'
import './IntroPanel.css'

const TOOLS_URL = 'https://raulesteveza.github.io/tools/'
const SOURCE_URL = 'https://github.com/RaulEstevezA/DataCleanr'
const platform = detectPlatform(navigator)

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
        {platform ? (
          <a className="button" href={downloadUrl(platform)}>
            {t.introDownloadFor(platform)}
          </a>
        ) : (
          <a className="button" href={RELEASES_URL} target="_blank" rel="noopener">
            {t.introDownload}
          </a>
        )}
        <a className="button" href={SOURCE_URL} target="_blank" rel="noopener">
          {t.introCode}
        </a>
        <a className="button" href={TOOLS_URL}>
          {t.introAllTools}
        </a>
      </div>

      <p className="intro__download-note">
        {t.introDownloadNote}{' '}
        <a href={t.introHowToOpenUrl} target="_blank" rel="noopener">
          {t.introHowToOpen}
        </a>
        {platform && (
          <>
            {' · '}
            <a href={RELEASES_URL} target="_blank" rel="noopener">
              {t.introOtherPlatforms}
            </a>
          </>
        )}
      </p>
    </section>
  )
}
