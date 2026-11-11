import { useState } from 'react'
import type { FormEvent } from 'react'
import { getErrorMessage } from '../../api/client'
import { useAuth } from '../../auth/useAuth'
import { navigate } from '../../app/navigation'

type LoginState = {
  username: string
  password: string
  submitting: boolean
  error: string | null
}

export function useLoginForm() {
  const auth = useAuth()
  const [state, setState] = useState<LoginState>({
    username: '',
    password: '',
    submitting: false,
    error: null,
  })

  const updateField = (field: 'username' | 'password', value: string) => {
    setState((previous) => ({ ...previous, [field]: value, error: null }))
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (state.submitting) return
    setState((previous) => ({ ...previous, submitting: true, error: null }))
    try {
      await auth.login(state.username.trim(), state.password)
      navigate('/')
    } catch (error) {
      setState((previous) => ({ ...previous, error: getErrorMessage(error) }))
    } finally {
      setState((previous) => ({ ...previous, submitting: false }))
    }
  }

  return { state, updateField, submit }
}
