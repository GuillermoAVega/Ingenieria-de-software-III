import { useEffect, useState } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import { getPaymentMethods } from '../payment-methods/api'
import type { PaymentMethod } from '../payment-methods/types'
import type { Invoice } from '../orders/types'
import { createVoucher, deleteVoucher, getInvoiceVouchers } from './api'
import { fromCents, parseAmount, toCents } from './money'
import { getPaymentStatus } from './status'
import type { PaymentVoucher, PaymentVoucherRow } from './types'

export type PaymentFormField = 'medioPagoId' | 'importe'

type PaymentVouchersState = {
  vouchers: PaymentVoucher[]
  methods: PaymentMethod[]
  loading: boolean
  error: string | null
  modalOpen: boolean
  medioPagoId: string
  importe: string
  saving: boolean
  formError: string | null
  fieldErrors: ApiFieldErrors
  deletingId: number | null
  reloadToken: number
}

const initialState: PaymentVouchersState = {
  vouchers: [],
  methods: [],
  loading: true,
  error: null,
  modalOpen: false,
  medioPagoId: '',
  importe: '',
  saving: false,
  formError: null,
  fieldErrors: {},
  deletingId: null,
  reloadToken: 0,
}

export function usePaymentVouchers(invoice: Invoice | null) {
  const [state, setState] = useState<PaymentVouchersState>(initialState)
  const invoiceId = invoice?.id ?? null

  useEffect(() => {
    if (invoiceId === null) return

    let cancelled = false

    async function loadVouchers(id: number) {
      try {
        const [vouchers, methods] = await Promise.all([getInvoiceVouchers(id), getPaymentMethods()])
        if (cancelled) return
        setState((previous) => ({ ...previous, vouchers, methods, loading: false, error: null }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          loading: false,
          error: getErrorMessage(requestError),
        }))
      }
    }

    void loadVouchers(invoiceId)

    return () => {
      cancelled = true
    }
  }, [invoiceId, state.reloadToken])

  const totalCents = toCents(invoice?.importe_total ?? 0)
  const paidCents = state.vouchers.reduce((sum, voucher) => sum + toCents(voucher.importe), 0)
  const balanceCents = Math.max(totalCents - paidCents, 0)

  const methodNames = new Map(state.methods.map((method) => [method.id, method.descripcion]))
  const rows: PaymentVoucherRow[] = state.vouchers.map((voucher) => ({
    ...voucher,
    medioPagoNombre: methodNames.get(voucher.medio_pago_id) ?? `Medio de pago #${voucher.medio_pago_id}`,
  }))

  const openModal = () => {
    setState((previous) => ({
      ...previous,
      modalOpen: true,
      medioPagoId: previous.methods.length === 1 ? String(previous.methods[0].id) : '',
      importe: balanceCents > 0 ? String(fromCents(balanceCents)) : '',
      formError: null,
      fieldErrors: {},
    }))
  }

  const closeModal = () => {
    setState((previous) => ({ ...previous, modalOpen: false, formError: null, fieldErrors: {} }))
  }

  const updateField = (field: PaymentFormField, value: string) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const reload = () => {
    setState((previous) => ({ ...previous, reloadToken: previous.reloadToken + 1 }))
  }

  const submit = async () => {
    if (invoiceId === null || state.saving) return

    const amount = parseAmount(state.importe)
    const fieldErrors: ApiFieldErrors = {}
    if (!state.medioPagoId) fieldErrors.medioPagoId = 'Elegí un medio de pago.'
    if (!Number.isFinite(amount) || toCents(amount) <= 0) {
      fieldErrors.importe = 'Ingresá un importe mayor a cero.'
    } else if (toCents(amount) > balanceCents) {
      fieldErrors.importe = `El importe supera el saldo pendiente (${fromCents(balanceCents).toLocaleString('es-AR')}).`
    }
    if (Object.keys(fieldErrors).length > 0) {
      setState((previous) => ({ ...previous, fieldErrors, formError: null }))
      return
    }

    setState((previous) => ({ ...previous, saving: true, formError: null, fieldErrors: {} }))
    try {
      await createVoucher({
        factura_id: invoiceId,
        medio_pago_id: Number(state.medioPagoId),
        importe: amount,
      })
      setState((previous) => ({ ...previous, saving: false, modalOpen: false }))
      reload()
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        saving: false,
        formError: getErrorMessage(requestError),
        fieldErrors: getFieldErrors(requestError),
      }))
    }
  }

  const remove = async (id: number) => {
    setState((previous) => ({ ...previous, deletingId: id, error: null }))
    try {
      await deleteVoucher(id)
      setState((previous) => ({ ...previous, deletingId: null }))
      reload()
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        deletingId: null,
        error: getErrorMessage(requestError),
      }))
    }
  }

  return {
    state,
    rows,
    total: fromCents(totalCents),
    paid: fromCents(paidCents),
    balance: fromCents(balanceCents),
    status: getPaymentStatus(fromCents(totalCents), fromCents(paidCents)),
    openModal,
    closeModal,
    updateField,
    submit,
    remove,
  }
}
