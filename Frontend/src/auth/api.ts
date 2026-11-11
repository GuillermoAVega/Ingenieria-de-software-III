import { apiFetch } from '../api/client'
import type { AuthUser, LoginResponse } from './types'

export function login(nombreUsuario: string, clave: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: { nombre_usuario: nombreUsuario, clave },
  })
}

export function getCurrentUser(): Promise<AuthUser> {
  return apiFetch<AuthUser>('/auth/me')
}
