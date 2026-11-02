const BASE: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function api<T = void>(
  path: string,
  opts: { method?: string; body?: unknown } = {},
): Promise<T> {
  let res: Response
  try {
    res = await fetch(BASE + path, {
      method: opts.method ?? 'GET',
      headers: opts.body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'No se pudo conectar con el servidor. ¿Está corriendo el backend?')
  }
  if (!res.ok) {
    let detail = `Error ${res.status}`
    try {
      const data = await res.json()
      if (typeof data.detail === 'string') detail = data.detail
      else if (Array.isArray(data.detail)) detail = 'Datos inválidos: revisá los campos del formulario'
    } catch {
      /* respuesta sin cuerpo JSON */
    }
    throw new ApiError(res.status, detail)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

// ---- Tipos (reflejan los schemas del backend) ----

export interface DetalleComanda {
  id: number
  comanda_id: number
  producto_id: number
  cantidad: number
  observaciones: string | null
  entregado: boolean
  activo: boolean
}

export interface Comanda {
  id: number
  fecha: string
  hora: string
  estado: 'abierta' | 'cerrada'
  mozo_id: number
  mesa_id: number
  cliente_id: number | null
  reserva_id: number | null
  activo: boolean
  detalles: DetalleComanda[]
}

export interface Factura {
  id: number
  comanda_id: number
  importe_total: number
  fecha_hora_emision: string
  activo: boolean
}

export interface DetalleFactura {
  id: number
  factura_id: number
  detalle_comanda_id: number | null
  promocion_id: number | null
  precio_unitario: number
  cantidad: number
  precio_final: number
  activo: boolean
}

export interface ComprobantePago {
  id: number
  factura_id: number
  medio_pago_id: number
  importe: number
  fecha_hora_emision: string
  activo: boolean
}

export interface MedioPago {
  id: number
  descripcion: string
  activo: boolean
}
