import { describe, expect, it } from 'vitest'
import { detectPlatform, downloadUrl } from './desktopDownload.ts'

describe('detectPlatform', () => {
  it.each([
    [{ platform: 'MacIntel', userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' }, 'macOS'],
    [{ platform: 'Win32', userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }, 'Windows'],
    [{ platform: 'Linux x86_64', userAgent: 'Mozilla/5.0 (X11; Linux x86_64)' }, 'Linux'],
  ])('detects desktop systems: %o', (navigator, expected) => {
    expect(detectPlatform(navigator)).toBe(expected)
  })

  it.each([
    { platform: 'Linux armv8l', userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) Mobile' },
    { platform: 'iPhone', userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)' },
    { platform: 'MacIntel', userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', maxTouchPoints: 5 },
    { platform: '', userAgent: 'Mozilla/5.0 (X11; CrOS x86_64 14541.0.0)' },
    { platform: '', userAgent: '' },
  ])('returns null for phones, tablets and unknown systems: %o', (navigator) => {
    expect(detectPlatform(navigator)).toBeNull()
  })
})

describe('downloadUrl', () => {
  it('points to the asset of the latest release', () => {
    expect(downloadUrl('macOS')).toBe(
      'https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-macOS.dmg',
    )
  })
})
