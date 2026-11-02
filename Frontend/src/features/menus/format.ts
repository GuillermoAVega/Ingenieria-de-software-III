/** Etiquetas y formatos compartidos por las pantallas de menús. */

const TIPO_LABELS: Record<string, string> = {
  plato: 'Plato',
  bebida: 'Bebida',
  postre: 'Postre',
  menu_ejecutivo: 'Menú ejecutivo',
  combo_promocion: 'Combo',
}

export function tipoLabel(tipo: string): string {
  return TIPO_LABELS[tipo] ?? tipo
}

/** Convierte `YYYY-MM-DD` en `dd/mm/aaaa` sin pasar por `Date` (evita el corrimiento UTC). */
export function formatDate(iso: string): string {
  const [year, month, day] = iso.split('-')
  if (!year || !month || !day) return iso
  return `${day}/${month}/${year}`
}

export function formatCurrency(value: string | number): string {
  return `$ ${Number(value).toLocaleString('es-AR')}`
}
