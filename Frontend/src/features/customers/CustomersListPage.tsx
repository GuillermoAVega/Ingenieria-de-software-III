/**
 * EQUIPO: Salón
 * FUNCIONALIDAD: Listado de clientes
 * Los datos de clientes se cargan desde la API; las visitas son estimaciones ficticias.
 */
import { useEffect, useMemo, useState } from 'react'
import { Alert, Button, Card, DataTable, DeleteButton, Input, PageHeader, Pagination, Select, Toolbar, ToolbarSpacer } from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { deleteCustomer, listCustomers } from './api'
import type { Customer } from './types'

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
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc')
  const [page, setPage] = useState(1)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const pageSize = 10

  useEffect(() => {
    listCustomers()
      .then(setCustomers)
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'No se pudieron cargar los clientes.'))
      .finally(() => setLoading(false))
  }, [])

  const filteredCustomers = useMemo(() => {
    const query = search.trim().toLocaleLowerCase()
    return customers
      .filter((customer) =>
        [customer.name, customer.phone, customer.dni].some((value) => value.toLocaleLowerCase().includes(query)),
      )
      .sort((first, second) => {
        const visitsDifference = first.visits - second.visits
        return (sortOrder === 'desc' ? -visitsDifference : visitsDifference) || first.name.localeCompare(second.name)
      })
  }, [customers, search, sortOrder])

  const visibleCustomers = filteredCustomers.slice((page - 1) * pageSize, page * pageSize)

  async function handleDelete(customer: Customer) {
    setError(null)
    try {
      await deleteCustomer(customer.dni)
      setCustomers((current) => current.filter((candidate) => candidate.dni !== customer.dni))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo eliminar el cliente.')
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
          <span className="muted text-sm">Visitas ficticias</span>
        </Toolbar>

        {error && <Alert tone="danger">{error}</Alert>}

        <DataTable
          columns={columns}
          rows={visibleCustomers}
          actions={(customer) => (
            <div className="row">
              <Button size="sm" onClick={() => navigate(`/clientes/${encodeURIComponent(customer.dni)}/editar`)}>
                Editar
              </Button>
              <DeleteButton
                title="Eliminar cliente"
                onConfirm={() => void handleDelete(customer)}
              >
                ¿Querés eliminar <strong>{customer.name}</strong>?
              </DeleteButton>
            </div>
          )}
          empty={<div className="empty"><span className="empty-title">{loading ? 'Cargando clientes...' : 'No hay clientes para mostrar'}</span></div>}
        />

        <Pagination
          page={page}
          pageSize={pageSize}
          total={filteredCustomers.length}
          onPageChange={setPage}
        />
      </Card>
    </>
  )
}
