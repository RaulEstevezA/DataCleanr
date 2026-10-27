import { useEffect, useState, type ReactNode } from 'react'
import { useI18n } from '../i18n/useI18n.ts'
import {
  detectArchitecture,
  detectPlatform,
  downloadUrl,
  hasArchitectureChoice,
  RELEASES_URL,
  type Architecture,
} from '../utils/desktopDownload.ts'
import './IntroPanel.css'

const TOOLS_URL = 'https://raulesteveza.github.io/tools/'
const SOURCE_URL = 'https://github.com/RaulEstevezA/DataCleanr'
const platform = detectPlatform(navigator)
const ARCHITECTURE_NAMES: Record<Architecture, string> = { x64: 'x64', arm64: 'ARM64' }

/** Presentation card shown before a file is loaded, styled like the portfolio's project windows. */
export function IntroPanel({ children }: { children: ReactNode }) {
  const { t } = useI18n()
  // x64 until the browser says otherwise; the note always links the other one in case it guessed wrong
  const [architecture, setArchitecture] = useState<Architecture>('x64')
  const choice = platform !== null && hasArchitectureChoice(platform)
  const otherArchitecture: Architecture = architecture === 'x64' ? 'arm64' : 'x64'

  useEffect(() => {
    if (!choice) return
    let active = true
    void detectArchitecture(navigator).then((detected) => {
      if (active && detected) setArchitecture(detected)
    })
    return () => {
      active = false
    }
  }, [choice])

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
          <a className="button" href={downloadUrl(platform, architecture)}>
            {t.introDownloadFor(architecture === 'arm64' && choice ? `${platform} ${ARCHITECTURE_NAMES.arm64}` : platform)}
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
        {platform && choice && (
          <>
            {' · '}
            <a href={downloadUrl(platform, otherArchitecture)}>{t.introOtherArchitecture(ARCHITECTURE_NAMES[otherArchitecture])}</a>
          </>
        )}
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
