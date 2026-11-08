import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import type { ApiFieldErrors } from '../../api/client'
import { ApiError, getErrorMessage, getFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { getBebidas, getPlatos, getPostres } from '../products/api'
import type { ComboComponente, ProductoBaseRespuesta } from '../products/api'
import { getSections } from '../sections/api'
import type { SeccionRespuesta } from '../sections/api'
import { createCombo, getCombo, updateCombo } from './api'
import { COMBO_SOURCES } from './types'
import type { ComboOption, ComboSource } from './types'

export type ComboFormValues = {
  nombre: string
  precio: string
  descripcion: string
  seccionId: string
  fecha_desde: string
  fecha_hasta: string
}

type ComboFormState = ComboFormValues & {
  /** Cantidad (como texto) por componente seleccionado, con clave `fuente:id`. */
  quantities: Record<string, string>
  options: ComboOption[]
  sections: SeccionRespuesta[]
  search: string
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

const SOURCE_LABELS: Record<ComboSource, string> = {
  platos: 'Plato',
  bebidas: 'Bebida',
  postres: 'Postre',
}

const QUANTITY_PREFIX = 'cantidad:'

const optionKey = (source: ComboSource, id: number) => `${source}:${id}`

function toOptions(source: ComboSource, items: ProductoBaseRespuesta[]): ComboOption[] {
  return items.map((item) => ({
    key: optionKey(source, item.id),
    nombre: item.nombre,
    tipoLabel: SOURCE_LABELS[source],
    dado_de_baja: item.dado_de_baja,
    source,
    productId: item.id,
    precio: Number(item.precio),
  }))
}

/** Cantidad entera >= 1 escrita como texto. */
function parseQuantity(value: string): number | null {
  const parsed = Number(value)
  return value.trim() !== '' && Number.isInteger(parsed) && parsed >= 1 ? parsed : null
}

function validate(state: ComboFormState): ApiFieldErrors {
  const errors: ApiFieldErrors = {}
  const precio = Number(state.precio)
  if (!state.nombre.trim()) errors.nombre = 'Ingresá un nombre para el combo.'
  else if (state.nombre.trim().length > 100) errors.nombre = 'El nombre no puede superar los 100 caracteres.'
  if (!state.precio.trim() || !Number.isFinite(precio) || precio <= 0) {
    errors.precio = 'El precio debe ser mayor a 0.'
  }
  if (!state.fecha_desde) errors.fecha_desde = 'Indicá la fecha de inicio.'
  if (!state.fecha_hasta) errors.fecha_hasta = 'Indicá la fecha de fin.'
  if (state.fecha_desde && state.fecha_hasta && state.fecha_desde > state.fecha_hasta) {
    errors.fecha_hasta = 'La fecha de fin no puede ser anterior a la de inicio.'
  }
  const keys = Object.keys(state.quantities)
  if (keys.length === 0) {
    errors.componentes = 'Seleccioná al menos un componente.'
  }
  keys.forEach((key) => {
    if (parseQuantity(state.quantities[key]) === null) {
      errors[`${QUANTITY_PREFIX}${key}`] = 'Ingresá un número entero mayor o igual a 1.'
    }
  })
  return errors
}

function toComponents(state: ComboFormState, source: ComboSource): ComboComponente[] {
  return state.options
    .filter((option) => option.source === source && option.key in state.quantities)
    .map((option) => ({
      id: option.productId,
      cantidad: parseQuantity(state.quantities[option.key]) ?? 1,
    }))
}

function toQuantities(
  quantities: Record<string, string>,
  source: ComboSource,
  items: ComboComponente[],
) {
  items.forEach((item) => {
    quantities[optionKey(source, item.id)] = String(item.cantidad)
  })
}

export function useComboForm(id?: string) {
  const numericId = id !== undefined ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0

  const [state, setState] = useState<ComboFormState>(() => ({
    nombre: '',
    precio: '',
    descripcion: '',
    seccionId: '',
    fecha_desde: '',
    fecha_hasta: '',
    quantities: {},
    options: [],
    sections: [],
    search: '',
    loading: true,
    saving: false,
    error: null,
    fieldErrors: {},
  }))

  useEffect(() => {
    let cancelled = false
    const comboId = isEditing ? numericId : null

    async function load() {
      try {
        // Un listado que falla no impide usar los demás
        const [platos, bebidas, postres, sections] = await Promise.allSettled([
          getPlatos(),
          getBebidas(),
          getPostres(),
          getSections(),
        ])
        const combo = comboId !== null ? await getCombo(comboId) : null
        if (cancelled) return
        const options = [
          ...(platos.status === 'fulfilled' ? toOptions('platos', platos.value) : []),
          ...(bebidas.status === 'fulfilled' ? toOptions('bebidas', bebidas.value) : []),
          ...(postres.status === 'fulfilled' ? toOptions('postres', postres.value) : []),
        ]
        const quantities: Record<string, string> = {}
        if (combo) {
          toQuantities(quantities, 'platos', combo.platos)
          toQuantities(quantities, 'bebidas', combo.bebidas)
          toQuantities(quantities, 'postres', combo.postres)
        }
        setState((previous) => ({
          ...previous,
          options,
          sections: sections.status === 'fulfilled' ? sections.value : [],
          ...(combo && {
            nombre: combo.nombre,
            precio: String(Number(combo.precio)),
            descripcion: combo.descripcion ?? '',
            seccionId: combo.seccion_id === null ? '' : String(combo.seccion_id),
            fecha_desde: combo.fecha_desde,
            fecha_hasta: combo.fecha_hasta,
            quantities,
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
              ? 'El combo que querés editar ya no existe.'
              : getErrorMessage(requestError),
        }))
      }
    }

    void load()

    return () => {
      cancelled = true
    }
  }, [isEditing, numericId])

  const updateField = (field: keyof ComboFormValues, value: string) => {
    setState((previous) => ({ ...previous, [field]: value }))
  }

  const updateSearch = (search: string) => {
    setState((previous) => ({ ...previous, search }))
  }

  // Agregar un componente ya presente no lo duplica: alternar lo quita
  const toggleComponent = (key: string) => {
    setState((previous) => {
      const quantities = { ...previous.quantities }
      if (key in quantities) delete quantities[key]
      else quantities[key] = '1'
      return { ...previous, quantities }
    })
  }

  const updateQuantity = (key: string, value: string) => {
    setState((previous) => ({
      ...previous,
      quantities: { ...previous.quantities, [key]: value },
    }))
  }

  const quantityError = (key: string) => state.fieldErrors[`${QUANTITY_PREFIX}${key}`]

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.loading || state.saving) return

    const fieldErrors = validate(state)
    if (Object.keys(fieldErrors).length > 0) {
      setState((previous) => ({ ...previous, fieldErrors, error: null }))
      return
    }

    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))

    const payload = {
      nombre: state.nombre.trim(),
      precio: Number(state.precio),
      descripcion: state.descripcion.trim() || null,
      seccion_id: state.seccionId === '' ? null : Number(state.seccionId),
      fecha_desde: state.fecha_desde,
      fecha_hasta: state.fecha_hasta,
      platos: toComponents(state, 'platos'),
      bebidas: toComponents(state, 'bebidas'),
      postres: toComponents(state, 'postres'),
    }

    try {
      if (isEditing && numericId !== null) {
        await updateCombo(numericId, payload)
      } else {
        await createCombo(payload)
      }
      navigate('/productos/combos')
    } catch (requestError) {
      setState((previous) => ({
        ...previous,
        error:
          requestError instanceof ApiError && requestError.status === 404
            ? 'El combo que querés editar ya no existe.'
            : getErrorMessage(requestError),
        fieldErrors: getFieldErrors(requestError),
      }))
    } finally {
      setState((previous) => ({ ...previous, saving: false }))
    }
  }

  // Suma de los componentes seleccionados con cantidad válida y ahorro frente al precio del combo
  const componentsTotal = state.options.reduce((total, option) => {
    const quantity = option.key in state.quantities ? parseQuantity(state.quantities[option.key]) : null
    return quantity === null ? total : total + option.precio * quantity
  }, 0)
  const comboPrice = Number(state.precio)
  const savings =
    state.precio.trim() !== '' && Number.isFinite(comboPrice) && comboPrice > 0
      ? componentsTotal - comboPrice
      : null

  return {
    state,
    isEditing,
    selectedKeys: Object.keys(state.quantities),
    componentsTotal,
    savings,
    sources: COMBO_SOURCES,
    updateField,
    updateSearch,
    toggleComponent,
    updateQuantity,
    quantityError,
    submit,
  }
}
