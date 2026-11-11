const TOKEN_KEY = 'gestion-restaurante-token'
export const AUTH_EXPIRED_EVENT = 'gestion-restaurante-auth-expired'

export function getAuthToken(): string | null {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function saveAuthToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearAuthToken(): void {
  window.localStorage.removeItem(TOKEN_KEY)
}
