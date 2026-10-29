export type WaiterStatus = 'activo' | 'inactivo'

export type Waiter = {
  id: string
  name: string
  phone: string
  email: string
  status: WaiterStatus
}
