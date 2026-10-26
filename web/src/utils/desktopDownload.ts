// Release assets keep the same names in every version (see .github/workflows/release-desktop.yml),
// so these links always point to the latest release.
export const RELEASES_URL = 'https://github.com/RaulEstevezA/DataCleanr/releases/latest'

export type DesktopPlatform = 'macOS' | 'Windows' | 'Linux'

const ASSETS: Record<DesktopPlatform, string> = {
  macOS: 'DataCleanr-macOS.dmg',
  Windows: 'DataCleanr-Windows.zip',
  Linux: 'DataCleanr-Linux.tar.gz',
}

export function downloadUrl(platform: DesktopPlatform): string {
  return `${RELEASES_URL}/download/${ASSETS[platform]}`
}

interface NavigatorInfo {
  userAgent: string
  platform?: string
  maxTouchPoints?: number
}

/** The visitor's desktop system, or null on phones, tablets and anything unknown. Only reads
 * the browser's own information: nothing is requested from GitHub until the button is clicked. */
export function detectPlatform({ userAgent, platform = '', maxTouchPoints = 0 }: NavigatorInfo): DesktopPlatform | null {
  const text = `${platform} ${userAgent}`
  if (/android|iphone|ipad|ipod|mobile/i.test(text)) return null
  // iPadOS presents itself as a Mac; a touch screen gives it away
  if (/mac/i.test(text)) return maxTouchPoints > 1 ? null : 'macOS'
  if (/win/i.test(text)) return 'Windows'
  if (/linux|x11/i.test(text) && !/cros/i.test(text)) return 'Linux'
  return null
}
