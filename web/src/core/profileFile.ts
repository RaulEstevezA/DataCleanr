/** "Clientes mensuales" -> "clientes-mensuales.datacleanr.json" */
export function profileFileName(name: string): string {
  const slug = name
    .normalize('NFD')
    .replace(/\p{M}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
  return `${slug || 'profile'}.datacleanr.json`
}
