export type Customer = {
  id: string
  dni: string
  name: string
  phone: string
  visits: number
  lastVisit: string
}

export type CustomerPayload = {
  dni: string
  nombre: string
  apellido: string
  telefono: string
}
