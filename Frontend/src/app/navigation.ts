/**
 * Navegación basada en hash, sin dependencias externas.
 * El hash es la única fuente de verdad de la ruta actual.
 */

export function normalizePath(path: string): string {
  const hashIndex = path.indexOf('#')
  let normalized = hashIndex >= 0 ? path.slice(hashIndex + 1) : path

  if (!normalized.startsWith('/')) {
    normalized = `/${normalized}`
  }

  if (normalized.length > 1 && normalized.endsWith('/')) {
    normalized = normalized.slice(0, -1)
  }

  return normalized || '/'
}

export function navigate(path: string): void {
  window.location.hash = `#${normalizePath(path)}`
}
