import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { getErrorMessage, getFieldErrors } from '../../api/client'
import type { ApiFieldErrors } from '../../api/client'
import { navigate } from '../../app/navigation'
import { createUser, getUser, updateUser } from './api'
import type { UserRole } from '../../auth/types'

type UserFormState = {
  nombre: string
  nombreUsuario: string
  clave: string
  rol: UserRole
  activo: boolean
  loading: boolean
  saving: boolean
  error: string | null
  fieldErrors: ApiFieldErrors
}

export function useUserForm(id?: string) {
  const numericId = id ? Number(id) : null
  const isEditing = numericId !== null && Number.isInteger(numericId) && numericId > 0
  const [state, setState] = useState<UserFormState>({
    nombre: '', nombreUsuario: '', clave: '', rol: 'operario', activo: true,
    loading: true, saving: false, error: null, fieldErrors: {},
  })

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const user = isEditing && numericId !== null ? await getUser(numericId) : null
        if (cancelled) return
        setState((previous) => ({
          ...previous,
          nombre: user?.nombre ?? '',
          nombreUsuario: user?.nombre_usuario ?? '',
          rol: user?.rol ?? 'operario',
          activo: user?.activo ?? true,
          loading: false,
        }))
      } catch (error) {
        if (!cancelled) setState((previous) => ({ ...previous, loading: false, error: getErrorMessage(error) }))
      }
    }
    void load()
    return () => { cancelled = true }
  }, [isEditing, numericId])

  const updateField = (field: 'nombre' | 'nombreUsuario' | 'clave' | 'rol' | 'activo', value: string | boolean) => {
    setState((previous) => ({ ...previous, [field]: value, error: null }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.saving || state.loading) return
    setState((previous) => ({ ...previous, saving: true, error: null, fieldErrors: {} }))
    const common = {
      nombre: state.nombre.trim(),
      nombre_usuario: state.nombreUsuario.trim(),
      rol: state.rol,
      activo: state.activo,
    }
    try {
      if (isEditing && numericId !== null) {
        await updateUser(numericId, state.clave ? { ...common, clave: state.clave } : common)
      } else {
        await createUser({ ...common, clave: state.clave })
      }
      navigate('/usuarios')
    } catch (error) {
      setState((previous) => ({
        ...previous,
        error: getErrorMessage(error),
        fieldErrors: getFieldErrors(error),
      }))
    } finally {
      setState((previous) => ({ ...previous, saving: false }))
    }
  }

  return { state, isEditing, updateField, submit }
}
