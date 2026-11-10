export type PaymentMethod = {
  id: number
  descripcion: string
  activo: boolean
}

export type PaymentMethodPayload = {
  descripcion: string
}
