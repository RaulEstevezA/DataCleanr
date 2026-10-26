import { useI18n } from '../i18n/useI18n.ts'
import './VisibleText.css'

/** Renders a cell value with whitespace made visible (one dot per space), so trims and collapses can be seen. */
export function VisibleText({ value }: { value: string }) {
  const { t } = useI18n()

  if (value === '') return <span className="visible-text__empty">{t.emptyCell}</span>

  return (
    <span className="visible-text">
      {value.split(/(\s+)/).map((part, i) =>
        /^\s+$/.test(part) ? (
          <span key={i} className="visible-text__space">
            {'·'.repeat(part.length)}
          </span>
        ) : (
          part
        ),
      )}
    </span>
  )
}
