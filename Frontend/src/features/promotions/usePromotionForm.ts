import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import {
  getBebidas,
  getCombos,
  getMenusEjecutivos,
  getPlatos,
  getPostres,
} from '../products/api'
import type { ProductoBaseRespuesta } from '../products/api'
import { createPromotion, getPromotion, updatePromotion } from './api'
import type { PromotionPayload, PromotionProductOption, PromotionType } from './types'

export type PromotionFormValues = {
  nombre: string
  tipo: PromotionType
  fecha_desde: string
  fecha_hasta: string
  descuento: string
  lleva: string
  paga: string
}

type PromotionFormState = PromotionFormValues & {
  productosIds: number[]
  products: PromotionProductOption[]
  search: string
  inUse: boolean
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

function toOptions(items: ProductoBaseRespuesta[], tipoLabel: string): PromotionProductOption[] {
  return items.map((item) => ({
    key: String(item.id),
    nombre: item.nombre,
    tipoLabel,
    dado_de_baja: item.dado_de_baja,
  }))
}

/** Combina los listados por tipo; un tipo que falla no impide usar los demás. */
async function loadProductOptions(): Promise<PromotionProductOption[]> {
  const sources: Array<[Promise<ProductoBaseRespuesta[]>, string]> = [
    [getPlatos(), 'Plato'],
    [getBebidas(), 'Bebida'],
    [getPostres(), 'Postre'],
    [getMenusEjecutivos(), 'Menú ejecutivo'],
    [getCombos(), 'Combo'],
  ]
  const results = await Promise.allSettled(sources.map(([request]) => request))
  const options: PromotionProductOption[] = []
  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      options.push(...toOptions(result.value, sources[index][1]))
    }
  })
  return options
}

function validate(state: PromotionFormValues & { productosIds: number[] }): ApiFieldErrors {
  const errors: ApiFieldErrors = {}
  const descuento = Number(state.descuento)
  if (!state.nombre.trim()) errors.nombre = 'Ingresá un nombre para la promoción.'
  else if (state.nombre.trim().length > 100) errors.nombre = 'El nombre no puede superar los 100 caracteres.'
  if (!state.fecha_desde) errors.fecha_desde = 'Indicá la fecha de inicio.'
  if (!state.fecha_hasta) errors.fecha_hasta = 'Indicá la fecha de fin.'
  if (state.fecha_desde && state.fecha_hasta && state.fecha_desde > state.fecha_hasta) {
    errors.fecha_hasta = 'La fecha de fin no puede ser anterior a la de inicio.'
  }
  if (state.tipo === 'porcentaje') {
    if (!state.descuento.trim() || !Number.isFinite(descuento) || descuento <= 0 || descuento > 100) {
      errors.descuento = 'El descuento debe ser un porcentaje mayor a 0 y hasta 100.'
    }
  } else {
    const lleva = Number(state.lleva)
    const paga = Number(state.paga)
    const llevaValid = state.lleva.trim() !== '' && Number.isInteger(lleva)
    const pagaValid = state.paga.trim() !== '' && Number.isInteger(paga)
    if (!llevaValid) errors.lleva = 'Indicá cuántas unidades se llevan (número entero).'
    if (!pagaValid || paga < 1) errors.paga = 'Indicá cuántas unidades se pagan (entero, mínimo 1).'
    if (llevaValid && pagaValid && paga >= 1 && lleva <= paga) {
      errors.lleva = 'Las unidades que se llevan deben ser más que las que se pagan.'
    }
  }
  if (state.productosIds.length === 0) {
    errors.productos_ids = 'Seleccioná al menos un producto.'
  }
  return errors
}

export function usePromotionForm(id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0

  const [state, setState] = useState<PromotionFormState>(() => ({
    nombre: '',
    tipo: 'porcentaje',
    fecha_desde: '',
    fecha_hasta: '',
    descuento: '',
    lleva: '',
    paga: '',
    productosIds: [],
    products: [],
    search: '',
    inUse: false,
    loading: true,
    saving: false,
    error: null,
    fieldErrors: {},
  }))

  useEffect(() => {
    let cancelled = false
    const promotionId = isEditing ? numericId : null

    async function load() {
      try {
        const [products, promotion] = await Promise.all([
          loadProductOptions(),
          promotionId !== null ? getPromotion(promotionId) : Promise.resolve(null),
        ])
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          products,
          ...(promotion && {
            nombre: promotion.nombre,
            fecha_desde: promotion.fecha_desde,
            fecha_hasta: promotion.fecha_hasta,
            tipo: promotion.tipo,
            descuento: promotion.descuento === null ? '' : String(promotion.descuento),
            lleva: promotion.lleva === null ? '' : String(promotion.lleva),
            paga: promotion.paga === null ? '' : String(promotion.paga),
            productosIds: promotion.productos_ids,
            inUse: promotion.en_uso,
          }),
          loading: false,
        }))
      } catch (requestError) {
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          loading: false,
          error:
            requestError instanceof ApiError && requestError.status === 404
              ? 'La promoción que querés editar ya no existe.'
              : getErrorMessage(requestError),
        }))
      }
    }

    void load()

    return () => {
      cancelled = true
    }
  }, [isEditing, numericId])

  const updateField = <K extends keyof PromotionFormValues>(
    field: K,
    value: PromotionFormValues[K],
  ) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search }))
  }

  const toggleProduct = (key: string) => {
    const productId = Number(key)
    setState((previous) => ({
      ...previous,
      productosIds: previous.productosIds.includes(productId)
        ? previous.productosIds.filter((current) => current !== productId)
        : [...previous.productosIds, productId],
    }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving || state.inUse) return

    const fieldErrors = validate(state)
    if (Object.keys(fieldErrors).length > 0) {
      setState((previous) => ({ ...previous, fieldErrors, error: null }))
      return
    }

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    const base = {
      nombre: state.nombre.trim(),
      tipo: state.tipo,
      fecha_desde: state.fecha_desde,
      fecha_hasta: state.fecha_hasta,
      productos_ids: state.productosIds,
    }
    const payload: PromotionPayload =
      state.tipo === 'porcentaje'
        ? { ...base, descuento: Number(state.descuento) }
        : { ...base, lleva: Number(state.lleva), paga: Number(state.paga) }

    try {
      if (isEditing && numericId !== null) {
        await updatePromotion(numericId, payload)
      } else {
        await createPromotion(payload)
      }
      navigate('/promociones')
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error:
          requestError instanceof ApiError && requestError.status === 404
            ? 'La promoción que querés editar ya no existe.'
            : getErrorMessage(requestError),
        fieldErrors: getFieldErrors(requestError),
      }))
    } finally {
      setState((previous) => ({ ...previous, saving: false }))
    }
  }

  return {
    state,
    options: state.products,
    isEditing,
    updateField,
    updateSearch,
    toggleProduct,
    submit,
  }
}
