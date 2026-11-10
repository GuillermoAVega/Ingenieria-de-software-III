/** Cálculos de importes en centavos para evitar errores de coma flotante. */

export function toCents(value: number | string): number {
  return Math.round(Number(value) * 100)
}

export function fromCents(cents: number): number {
  return cents / 100
}

/** Interpreta lo que escribe el usuario ("5000", "5000,50", "5.000,50"); NaN si no es un número. */
export function parseAmount(text: string): number {
  const trimmed = text.trim()
  if (!trimmed) return Number.NaN
  const normalized = trimmed.includes(',')
    ? trimmed.replace(/\./g, '').replace(',', '.')
    : trimmed
  return Number(normalized)
}
