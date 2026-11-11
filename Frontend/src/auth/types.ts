export type UserRole = 'administrador' | 'operario'

export type AuthUser = {
  id: number
  nombre: string
  nombre_usuario: string
  rol: UserRole
  activo: boolean
}

export type LoginResponse = {
  token: string
  tipo: 'bearer'
  usuario: AuthUser
}
