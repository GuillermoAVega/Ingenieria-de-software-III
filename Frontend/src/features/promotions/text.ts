/** Minúsculas y sin tildes, para comparar nombres sin distinguir acentos. */
export function normalizeText(text: string): string {
  return text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()
}
