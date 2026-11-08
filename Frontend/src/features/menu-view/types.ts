import type { MenuViewData } from './api'

export type MenuViewItem = {
  key: string
  nombre: string
  descripcion: string | null
  precio: string
  seccionId: number | null
  platoNombre?: string
  postreNombre?: string
}

export type MenuViewSectionGroup = {
  id: number
  nombre: string
  subtitulo: string | null
  items: MenuViewItem[]
}

export type MenuViewState = {
  date: string
  loading: boolean
  error: string | null
  data: MenuViewData | null
}
