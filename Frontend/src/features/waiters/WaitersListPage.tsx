import { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Badge,
  Button,
  Card,
  DataTable,
  DeleteButton,
  Input,
  PageHeader,
  Pagination,
  Select,
  Toolbar,
  ToolbarSpacer,
} from '../../ui/ui'
import type { DataTableColumn } from '../../ui/ui'
import { navigate } from '../../app/navigation'
import { deactivateWaiter, listWaiters, reactivateWaiter } from './api'
import type { Waiter } from './types'

type StatusFilter = 'todos' | 'activos' | 'inactivos'

const pageSize = 10

const columns: DataTableColumn<Waiter>[] = [
  {
    key: 'name',
    header: 'Mozo',
    render: (waiter) => <span className="cell-main">{waiter.name}</span>,
  },
  {
    key: 'nro_legajo',
    header: 'N.º de legajo',
    num: true,
  },
  {
    key: 'estado',
    header: 'Estado',
    render: (waiter) => (
      <Badge tone={waiter.estado ? 'success' : 'neutral'}>
        {waiter.estado ? 'Activo' : 'Inactivo'}
      </Badge>
    ),
  },
]

export function WaitersListPage() {
  const [waiters, setWaiters] = useState<Waiter[]>([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<StatusFilter>('todos')
  const [page, setPage] = useState(1)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    listWaiters()
      .then((result) => {
        if (!cancelled) setWaiters(result)
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError(cause instanceof Error ? cause.message : 'No se pudieron cargar los mozos.')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const filteredWaiters = useMemo(() => {
    const query = search.trim().toLocaleLowerCase()
    return waiters.filter((waiter) => {
      const matchesSearch =
        waiter.name.toLocaleLowerCase().includes(query) ||
        String(waiter.nro_legajo).includes(query)
      const matchesStatus =
        status === 'todos' ||
        (status === 'activos' && waiter.estado) ||
        (status === 'inactivos' && !waiter.estado)
      return matchesSearch && matchesStatus
    })
  }, [waiters, search, status])

  const lastPage = Math.max(1, Math.ceil(filteredWaiters.length / pageSize))
  const currentPage = Math.min(page, lastPage)
  const visibleWaiters = filteredWaiters.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  async function handleDeactivate(waiter: Waiter) {
    setError(null)
    try {
      await deactivateWaiter(waiter.id)
      setWaiters((current) =>
        current.map((candidate) =>
          candidate.id === waiter.id ? { ...candidate, estado: false } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo dar de baja al mozo.')
    }
  }

  async function handleReactivate(waiter: Waiter) {
    setError(null)
    try {
      await reactivateWaiter(waiter.id)
      setWaiters((current) =>
        current.map((candidate) =>
          candidate.id === waiter.id ? { ...candidate, estado: true } : candidate,
        ),
      )
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'No se pudo reactivar al mozo.')
    }
  }

  return (
    <>
      <PageHeader
        title="Mozos"
        subtitle="Equipo de salón, número de legajo y estado de cada mozo."
        actions={
          <Button variant="primary" onClick={() => navigate('/mozos/nuevo')}>
            Nuevo mozo
          </Button>
        }
      />

      <Card flush>
        <Toolbar>
          <Input
            aria-label="Buscar mozos por nombre o número de legajo"
            placeholder="Buscar por nombre o legajo..."
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
          />
          <Select
            aria-label="Filtrar mozos por estado"
            value={status}
            onChange={(event) => {
              const nextStatus = event.target.value
              setStatus(
                nextStatus === 'activos' || nextStatus === 'inactivos' ? nextStatus : 'todos',
              )
              setPage(1)
            }}
          >
            <option value="todos">Todos los estados</option>
            <option value="activos">Activos</option>
            <option value="inactivos">Inactivos</option>
          </Select>
          <ToolbarSpacer />
          <span className="muted text-sm">Mostrando {filteredWaiters.length} mozos</span>
        </Toolbar>

        {error && <Alert tone="danger">{error}</Alert>}

        <DataTable
          columns={columns}
          rows={visibleWaiters}
          rowKey="id"
          actions={(waiter) => (
            <div className="row">
              {waiter.estado ? (
                <>
                  <Button size="sm" onClick={() => navigate(`/mozos/${waiter.id}/editar`)}>
                    Editar
                  </Button>
                  <DeleteButton
                    label="Dar de baja"
                    title="Dar de baja mozo"
                    confirmLabel="Dar de baja"
                    onConfirm={() => void handleDeactivate(waiter)}
                  >
                    ¿Querés dar de baja a <strong>{waiter.name}</strong>?
                  </DeleteButton>
                </>
              ) : (
                <Button size="sm" onClick={() => void handleReactivate(waiter)}>
                  Reactivar
                </Button>
              )}
            </div>
          )}
          empty={
            <div className="empty">
              <span className="empty-title">
                {loading ? 'Cargando mozos...' : 'No hay mozos para mostrar'}
              </span>
            </div>
          }
        />

        <Pagination
          page={currentPage}
          pageSize={pageSize}
          total={filteredWaiters.length}
          onPageChange={setPage}
        />
      </Card>
    </>
  )
}
