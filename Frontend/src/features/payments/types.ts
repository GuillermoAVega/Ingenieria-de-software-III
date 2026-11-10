export type PaymentVoucher = {
  id: number
  factura_id: number
  medio_pago_id: number
  importe: number
  fecha_hora_emision: string
  activo: boolean
}

export type PaymentVoucherPayload = {
  factura_id: number
  medio_pago_id: number
  importe: number
}

export type PaymentStatus = 'pagada' | 'parcial' | 'sin_pagar'

export type PaymentVoucherRow = PaymentVoucher & {
  medioPagoNombre: string
}
