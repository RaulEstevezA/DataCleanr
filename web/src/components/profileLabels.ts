import type { CellAction } from '../core/operation.ts'
import type { ProfileStep } from '../core/profile.ts'
import type { Messages } from '../i18n/messages.ts'

export function actionName(t: Messages, action: CellAction): string {
  switch (action) {
    case 'custom':
      return t.customReplace
    case 'phone':
      return t.normalizePhone
    case 'date':
      return t.normalizeDate
    case 'amount':
      return t.normalizeAmount
    case 'similar':
      return t.similarValues
    default:
      return t.transformNames[action]
  }
}

/** Human description of a profile step, e.g. "Trim spaces in “Contacto”". */
export function describeProfileStep(t: Messages, step: ProfileStep): string {
  switch (step.type) {
    case 'removeDuplicates':
      return t.profileStepDuplicates(step.columns.join(', '))
    case 'map':
      return t.profileStepMap(step.column, step.mapping.length)
    case 'transform':
      return t.profileStepCells(actionName(t, step.transform), step.column)
    case 'replace':
      return t.profileStepCells(actionName(t, 'custom'), step.column)
    default:
      return t.profileStepCells(actionName(t, step.type), step.column)
  }
}
