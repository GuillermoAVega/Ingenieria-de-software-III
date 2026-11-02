/** Utilidades de formato compartidas por cualquier pantalla de la aplicación. */

/** Moneda en pesos argentinos. Acepta números o strings numéricos del backend. */
export function formatCurrency(value: number | string): string {
  return `$ ${Number(value).toLocaleString('es-AR')}`
}

/** Fecha actual en formato `YYYY-MM-DD` usando la zona horaria local. */
export function todayISO(): string {
  return new Date().toLocaleDateString('sv-SE')
}

/** Hora actual en formato `HH:MM`. */
export function currentTime(): string {
  return new Date().toTimeString().slice(0, 5)
}

/**
 * Convierte una fecha `YYYY-MM-DD` en `dd/mm/aaaa` sin pasar por `Date`.
 * Evita el corrimiento de día por zona horaria.
 */
export function formatDate(value: string): string {
  const [year, month, day] = value.split('T')[0]?.split('-') ?? []
  if (!year || !month || !day) return value
  return `${day}/${month}/${year}`
}

/** Normaliza una hora `HH:MM:SS` o `HH:MM` a `HH:MM`. */
export function formatTime(value: string): string {
  return value.slice(0, 5)
}

/** Fecha y hora legibles para valores ISO completos. */
export function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })
}
