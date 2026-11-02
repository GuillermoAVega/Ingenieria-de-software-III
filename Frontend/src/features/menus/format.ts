/** Etiquetas y formatos compartidos por las pantallas de menús. */

export { formatCurrency, formatDate } from '../../utils/format'

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
