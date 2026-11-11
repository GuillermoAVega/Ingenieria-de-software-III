import { createContext } from 'react'
import type { AuthUser } from './types'

export type AuthState = {
  user: AuthUser | null
  loading: boolean
}

export type AuthContextValue = AuthState & {
  login: (nombreUsuario: string, clave: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
