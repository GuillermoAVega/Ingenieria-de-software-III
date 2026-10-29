/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Listado de clientes
 * Los datos de clientes se cargan desde la API; las visitas son estimaciones ficticias.
 */
import { useEffect, useMemo, useState } from 'react'
import { Alert, Badge, Button, Card, DataTable, DeleteButton, Input, PageHeader, Pagination, Select, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { deleteCustomer, listCustomers, reactivateCustomer } from './api'
import type { Customer } from './types'

type StatusFilter = 'todos' | 'activos' | 'inactivos'

const pageSize = 10

const columns: DataTableColumn<Customer>[] = [
  {
    key: 'name',
    header: 'Cliente',
    render: (customer) => <span className="cell-main">{customer.name}</span>,
  },
  {
    key: 'dni',
    header: 'DNI',
  },
  {
    key: 'phone',
    header: 'Teléfono',
  },
  {
    key: 'estado',
    header: 'Estado',
    render: (customer) => (
      <Badge tone={customer.estado ? 'success' : 'neutral'}>
        {customer.estado ? 'Activo' : 'Inactivo'}
      </Badge>
    ),
  },
  {
    key: 'visits',
    header: 'Visitas ficticias',
    num: true,
  },
  {
    key: 'lastVisit',
    header: 'Última visita',
  },
]

export function CustomersListPage() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<StatusFilter>('todos')
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc')
  const [page, setPage] = useState(1)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    listCustomers()
      .then((result) => {
        if (!cancelled) setCustomers(result)
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : 'No se pudieron cargar los clientes.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const filteredCustomers = useMemo(() => {
    const query = search.trim().toLocaleLowerCase()
    return customers
      .filter((customer) => {
        const matchesSearch = [customer.name, customer.phone, customer.dni]
          .some((value) => value.toLocaleLowerCase().includes(query))
        const matchesStatus =
          status === 'todos' ||
          (status === 'activos' && customer.estado) ||
          (status === 'inactivos' && !customer.estado)
        return matchesSearch && matchesStatus
      })
      .sort((first, second) => {
        const visitsDifference = first.visits - second.visits
        return (sortOrder === 'desc' ? -visitsDifference : visitsDifference) || first.name.localeCompare(second.name)
      })
  }, [customers, search, sortOrder, status])

  const currentPage = Math.min(page, Math.max(1, Math.ceil(filteredCustomers.length / pageSize)))
  const visibleCustomers = filteredCustomers.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  async function handleDelete(customer: Customer) {
    setError(null)
    try {
      await deleteCustomer(customer.dni)
      setCustomers((current) =>
        current.map((candidate) =>
          candidate.dni === customer.dni ? { ...candidate, estado: false } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo eliminar el cliente.')
    }
  }

  async function handleReactivate(customer: Customer) {
    setError(null)
    try {
      await reactivateCustomer(customer.dni)
      setCustomers((current) =>
        current.map((candidate) =>
          candidate.dni === customer.dni ? { ...candidate, estado: true } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo reactivar al cliente.')
    }
  }

  return (
    <>
      <PageHeader
        title="Clientes"
        subtitle="Ficha de clientes frecuentes, contacto y visitas estimadas."
        actions={
          <Button variant="primary" onClick={() => navigate('/clientes/nuevo')}>
            Nuevo cliente
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            placeholder="Buscar por nombre, teléfono o DNI..."
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
          />
          <Select
            aria-label="Filtrar clientes por estado"
            value={status}
            onChange={(event) => {
              const nextStatus = event.target.value
              setStatus(nextStatus === 'activos' || nextStatus === 'inactivos' ? nextStatus : 'todos')
              setPage(1)
            }}
          >
            <option value="todos">Todos los estados</option>
            <option value="activos">Activos</option>
            <option value="inactivos">Inactivos</option>
          </Select>
          <Select
            aria-label="Ordenar por visitas"
            value={sortOrder}
            onChange={(event) => {
              setSortOrder(event.target.value === 'asc' ? 'asc' : 'desc')
              setPage(1)
            }}
          >
            <option value="desc">Más visitas</option>
            <option value="asc">Menos visitas</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Mostrando {filteredCustomers.length} clientes · visitas ficticias</span>
        </Toolbar>

        {error && <Alert tone="danger">{error}</Alert>}

        <DataTable
          columns={columns}
          rows={visibleCustomers}
          actions={(customer) => (
            <div className="row">
              {customer.estado ? (
                <>
                  <Button size="sm" onClick={() => navigate(`/clientes/${encodeURIComponent(customer.dni)}/editar`)}>
                    Editar
                  </Button>
                  <DeleteButton
                    label="Dar de baja"
                    title="Dar de baja cliente"
                    confirmLabel="Dar de baja"
                    onConfirm={() => void handleDelete(customer)}
                  >
                    ¿Querés dar de baja a <strong>{customer.name}</strong>?
                  </DeleteButton>
                </>
              ) : (
                <Button size="sm" onClick={() => void handleReactivate(customer)}>
                  Reactivar
                </Button>
              )}
            </div>
          )}
          empty={<div className="empty"><span className="empty-title">{loading ? 'Cargando clientes...' : 'No hay clientes para mostrar'}</span></div>}
        />

        <Pagination
          page={currentPage}
          pageSize={pageSize}
          total={filteredCustomers.length}
          onPageChange={setPage}
        />
      </Card>
    </>
  )
}
