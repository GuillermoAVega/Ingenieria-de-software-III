export type ReservationStatus = 'confirmada' | 'con-comanda' | 'cancelada' | 'ausente' | 'pendiente'

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
