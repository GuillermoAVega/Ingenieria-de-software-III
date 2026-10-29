export type ReservationStatus = 'pendiente' | 'con_comanda' | 'cancelada' | 'ausente'

export type Reservation = {
  id: string
  time: string
  date: string
  customer: string
  phone: string
  guests: number
  table: string
  status: ReservationStatus
}

export type CustomerRecord = {
  id: number
  dni: string
  nombre: string
  apellido: string
  telefono: string
  estado: boolean
}

export type TableRecord = {
  id: number
  capacidad: number
  disponible: boolean
  sector_id: number
  estado: boolean
}

export type ReservationDetail = {
  reserva_id: number
  producto_id: number
  cantidad_producto: number
}

export type ReservationRecord = {
  id: number
  fecha: string
  hora: string
  cant_comensales: number
  observaciones: string | null
  cliente_id: number
  estado: ReservationStatus
  mesa_ids: number[]
  detalles: ReservationDetail[]
}

export type ReservationPayload = {
  fecha: string
  hora: string
  cant_comensales: number
  observaciones: string | null
  cliente_id: number
}

export type ReservationUpdatePayload = ReservationPayload & {
  estado: ReservationStatus
}

export type ReservationDetailPayload = {
  producto_id: number
  cantidad_producto: number
}

export type CustomerPayload = {
  dni: string
  nombre: string
  apellido: string
  telefono: string
}
