import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { getCurrentUser, login as requestLogin } from './api'
import {
  AUTH_EXPIRED_EVENT,
  clearAuthToken,
  getAuthToken,
  saveAuthToken,
} from './session'
import { AuthContext } from './context'
import type { AuthContextValue, AuthState } from './context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, loading: true })

  useEffect(() => {
    let cancelled = false

    async function restoreSession() {
      if (!getAuthToken()) {
        setState({ user: null, loading: false })
        return
      }
      try {
        const user = await getCurrentUser()
        if (!cancelled) setState({ user, loading: false })
      } catch {
        clearAuthToken()
        if (!cancelled) setState({ user: null, loading: false })
      }
    }

    const handleExpired = () => {
      clearAuthToken()
      setState({ user: null, loading: false })
    }

    window.addEventListener(AUTH_EXPIRED_EVENT, handleExpired)
    void restoreSession()
    return () => {
      cancelled = true
      window.removeEventListener(AUTH_EXPIRED_EVENT, handleExpired)
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login: async (nombreUsuario, clave) => {
        const response = await requestLogin(nombreUsuario, clave)
        saveAuthToken(response.token)
        setState({ user: response.usuario, loading: false })
      },
      logout: () => {
        clearAuthToken()
        setState({ user: null, loading: false })
      },
    }),
    [state],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
