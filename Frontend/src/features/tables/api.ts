import type { SectorPayload, SectorRecord, TablePayload, TableRecord } from './types'
import { apiFetch } from '../../api/client'

export async function listSectors(): Promise<SectorRecord[]> {
  return apiFetch<SectorRecord[]>('/sectores/')
}

export async function getSector(id: number): Promise<SectorRecord> {
  return apiFetch<SectorRecord>(`/sectores/${id}`)
}

export async function createSector(sector: SectorPayload): Promise<void> {
  await apiFetch('/sectores/', { method: 'POST', body: sector })
}

export async function updateSector(id: number, sector: SectorPayload): Promise<void> {
  await apiFetch(`/sectores/${id}`, { method: 'PUT', body: sector })
}

export async function deactivateSector(id: number): Promise<void> {
  await apiFetch(`/sectores/${id}`, { method: 'DELETE' })
}

export async function reactivateSector(id: number): Promise<void> {
  await apiFetch(`/sectores/${id}/reactivar`, { method: 'PATCH' })
}

export async function listTables(incluirInactivas = false): Promise<TableRecord[]> {
  const query = incluirInactivas ? '?incluir_inactivas=true' : ''
  return apiFetch<TableRecord[]>(`/mesas${query}`)
}

export async function getTable(id: number): Promise<TableRecord> {
  return apiFetch<TableRecord>(`/mesas/${id}`)
}

export async function createTable(table: TablePayload): Promise<void> {
  await apiFetch('/mesas', { method: 'POST', body: table })
}

export async function updateTable(id: number, table: TablePayload): Promise<void> {
  await apiFetch(`/mesas/${id}`, { method: 'PUT', body: table })
}

export async function deactivateTable(id: number): Promise<void> {
  await apiFetch(`/mesas/${id}`, { method: 'DELETE' })
}

export async function reactivateTable(id: number): Promise<void> {
  await apiFetch(`/mesas/${id}/reactivar`, { method: 'PATCH' })
}
