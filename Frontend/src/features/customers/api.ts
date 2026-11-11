import { generateFakeVisitData } from './demo'
import type { Customer, CustomerPayload } from './types'
import { apiFetch } from '../../api/client'

type CustomerResponse = CustomerPayload & {
  id: number
  estado: boolean
}

function toCustomer(response: CustomerResponse): Customer {
  const fakeVisits = generateFakeVisitData(response.dni)
  return {
    id: response.dni,
    dni: response.dni,
    name: `${response.nombre} ${response.apellido}`,
    phone: response.telefono,
    estado: response.estado,
    ...fakeVisits,
  }
}

export async function listCustomers(): Promise<Customer[]> {
  const customers = await apiFetch<CustomerResponse[]>('/clientes')
  return customers.map(toCustomer)
}

export async function getCustomer(dni: string): Promise<CustomerResponse> {
  return apiFetch<CustomerResponse>(`/clientes/${encodeURIComponent(dni)}`)
}

export async function createCustomer(customer: CustomerPayload): Promise<void> {
  await apiFetch('/clientes', { method: 'POST', body: customer })
}

export async function updateCustomer(dni: string, customer: CustomerPayload): Promise<void> {
  await apiFetch(`/clientes/${encodeURIComponent(dni)}`, { method: 'PUT', body: customer })
}

export async function deleteCustomer(dni: string): Promise<void> {
  await apiFetch(`/clientes/${encodeURIComponent(dni)}`, { method: 'DELETE' })
}

export async function reactivateCustomer(dni: string): Promise<void> {
  await apiFetch(`/clientes/${encodeURIComponent(dni)}/reactivar`, { method: 'PATCH' })
}
