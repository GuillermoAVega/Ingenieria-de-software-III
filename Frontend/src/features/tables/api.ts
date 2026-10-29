import type { SectorPayload, SectorRecord, TablePayload, TableRecord } from './types'

const API_BASE_URL = 'http://localhost:8000'

async function request(path: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers)
  if (init?.body) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    const body = await response.text()
    let message = body
    try {
      const error = JSON.parse(body) as { detail?: unknown }
      if (typeof error.detail === 'string') {
        message = error.detail
      } else if (Array.isArray(error.detail)) {
        message = error.detail
          .map((item) => (typeof item === 'object' && item !== null && 'msg' in item ? item.msg : ''))
          .filter(Boolean)
          .join('. ')
      }
    } catch {
      // Si la respuesta no es JSON, se muestra el texto devuelto por el servidor.
    }

    throw new Error(message || `Error al comunicarse con el servidor (${response.status}).`)
  }

  return response
}

export async function listSectors(): Promise<SectorRecord[]> {
  const response = await request('/sectores/')
  return (await response.json()) as SectorRecord[]
}

export async function getSector(id: number): Promise<SectorRecord> {
  const response = await request(`/sectores/${id}`)
  return (await response.json()) as SectorRecord
}

export async function createSector(sector: SectorPayload): Promise<void> {
  await request('/sectores/', {
    method: 'POST',
    body: JSON.stringify(sector),
  })
}

export async function updateSector(id: number, sector: SectorPayload): Promise<void> {
  await request(`/sectores/${id}`, {
    method: 'PUT',
    body: JSON.stringify(sector),
  })
}

export async function deactivateSector(id: number): Promise<void> {
  await request(`/sectores/${id}`, { method: 'DELETE' })
}

export async function reactivateSector(id: number): Promise<void> {
  await request(`/sectores/${id}/reactivar`, { method: 'PATCH' })
}

export async function listTables(incluirInactivas = false): Promise<TableRecord[]> {
  const query = incluirInactivas ? '?incluir_inactivas=true' : ''
  const response = await request(`/mesas${query}`)
  return (await response.json()) as TableRecord[]
}

export async function getTable(id: number): Promise<TableRecord> {
  const response = await request(`/mesas/${id}`)
  return (await response.json()) as TableRecord
}

export async function createTable(table: TablePayload): Promise<void> {
  await request('/mesas', {
    method: 'POST',
    body: JSON.stringify(table),
  })
}

export async function updateTable(id: number, table: TablePayload): Promise<void> {
  await request(`/mesas/${id}`, {
    method: 'PUT',
    body: JSON.stringify(table),
  })
}

export async function deactivateTable(id: number): Promise<void> {
  await request(`/mesas/${id}`, { method: 'DELETE' })
}

export async function reactivateTable(id: number): Promise<void> {
  await request(`/mesas/${id}/reactivar`, { method: 'PATCH' })
}
