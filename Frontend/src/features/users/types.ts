import type { AuthUser, UserRole } from '../../auth/types'

export type UserRecord = AuthUser

export type UserPayload = {
  nombre: string
  nombre_usuario: string
  clave?: string
  rol: UserRole
  activo?: boolean
}
