/**
 * Cliente HTTP de la aplicación.
 *
 * La URL base del backend se configura en `VITE_API_BASE_URL` (Frontend/.env).
 * Las rutas se escriben sin la barra inicial duplicada, por ejemplo `/secciones/1`.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '')

export type ApiFetchOptions = Omit<RequestInit, 'body'> & {
  body?: unknown
}

export type ApiFieldErrors = Record<string, string>

type DetailEntry = {
  loc?: Array<string | number>
  msg?: string
  type?: string
  [key: string]: unknown
}

/** Error HTTP con el cuerpo original devuelto por el backend. */
export class ApiError extends Error {
  status: number
  detail: unknown
  body: unknown

  constructor(status: number, message: string, detail: unknown, body: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
    this.body = body
  }
}

function joinPath(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${BASE_URL}${normalized}`
}

function extractMessage(body: unknown): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail

    if (typeof detail === 'string' && detail.trim()) {
      return detail
    }

    if (Array.isArray(detail)) {
      const mensajes = detail
        .map((entrada) => {
          if (entrada && typeof entrada === 'object' && 'msg' in entrada) {
            const mensaje = (entrada as DetailEntry).msg
            return typeof mensaje === 'string' ? mensaje : null
          }
          return typeof entrada === 'string' ? entrada : null
        })
        .filter((mensaje): mensaje is string => Boolean(mensaje))

      if (mensajes.length) {
        return mensajes.join(' ')
      }
    }
  }

  return 'No se pudo completar la operación con el servidor.'
}

async function readResponseBody(response: Response): Promise<unknown> {
  const texto = await response.text()
  if (!texto) {
    return null
  }

  try {
    return JSON.parse(texto)
  } catch {
    return texto
  }
}

/**
 * Realiza una petición al backend y devuelve el JSON tipado.
 * Lanza `ApiError` ante respuestas HTTP no exitosas y conserva el cuerpo del error.
 */
export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { body, headers, ...rest } = options
  const finalHeaders = new Headers(headers)

  let payload: BodyInit | undefined
  if (body instanceof FormData) {
    payload = body
  } else if (body !== undefined) {
    if (!finalHeaders.has('Content-Type')) {
      finalHeaders.set('Content-Type', 'application/json')
    }
    payload = JSON.stringify(body)
  }

  let response: Response
  try {
    response = await fetch(joinPath(path), {
      ...rest,
      headers: finalHeaders,
      body: payload,
    })
  } catch {
    throw new ApiError(
      0,
      'No se pudo conectar con el servidor. Verificá que el backend esté en ejecución.',
      null,
      null,
    )
  }

  if (!response.ok) {
    const errorBody = await readResponseBody(response)
    throw new ApiError(response.status, extractMessage(errorBody), errorBody, errorBody)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const responseBody = await readResponseBody(response)
  return responseBody as T
}

/** Devuelve un mensaje legible para cualquier error capturado en una pantalla. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'Ocurrió un error inesperado.'
}

/**
 * Traduce los errores de campo de FastAPI/Pydantic a un mapa por nombre de campo.
 * Ejemplo: `body.nombre` se expone como `nombre`.
 */
export function getFieldErrors(error: unknown): ApiFieldErrors {
  if (!(error instanceof ApiError)) {
    return {}
  }

  const detail = error.detail
  if (!detail || typeof detail !== 'object' || !('detail' in detail)) {
    return {}
  }

  const entradas = (detail as { detail: unknown }).detail
  if (!Array.isArray(entradas)) {
    return {}
  }

  const errores: ApiFieldErrors = {}
  for (const entrada of entradas) {
    if (!entrada || typeof entrada !== 'object') {
      continue
    }

    const { loc, msg } = entrada as DetailEntry
    if (!Array.isArray(loc) || typeof msg !== 'string') {
      continue
    }

    const campo = [...loc].reverse().find((parte) => typeof parte === 'string')
    if (typeof campo === 'string' && !errores[campo]) {
      errores[campo] = msg
    }
  }

  return errores
}
