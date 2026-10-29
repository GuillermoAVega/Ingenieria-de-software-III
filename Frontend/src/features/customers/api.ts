import { generateFakeVisitData } from './demo'
import type { Customer, CustomerPayload } from './types'

type CustomerResponse = CustomerPayload & {
  id: number
  estado: boolean
}

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
  const response = await request('/clientes')
  const customers = (await response.json()) as CustomerResponse[]
  return customers.map(toCustomer)
}

export async function getCustomer(dni: string): Promise<CustomerResponse> {
  const response = await request(`/clientes/${encodeURIComponent(dni)}`)
  return (await response.json()) as CustomerResponse
}

export async function createCustomer(customer: CustomerPayload): Promise<void> {
  await request('/clientes', {
    method: 'POST',
    body: JSON.stringify(customer),
  })
}

export async function updateCustomer(dni: string, customer: CustomerPayload): Promise<void> {
  await request(`/clientes/${encodeURIComponent(dni)}`, {
    method: 'PUT',
    body: JSON.stringify(customer),
  })
}

export async function deleteCustomer(dni: string): Promise<void> {
  await request(`/clientes/${encodeURIComponent(dni)}`, { method: 'DELETE' })
}

export async function reactivateCustomer(dni: string): Promise<void> {
  await request(`/clientes/${encodeURIComponent(dni)}/reactivar`, { method: 'PATCH' })
}
