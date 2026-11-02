import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type FormEvent,
  type ReactNode,
} from 'react'

// ---- Formato ----
export const money = (n: number) =>
  '$ ' + n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
export const hhmm = (t: string) => t.slice(0, 5)
export const fechaCorta = (iso: string) =>
  new Date(iso).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })

// ---- Carga de datos ----
export function useLoad<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState('')
  const [tick, setTick] = useState(0)
  useEffect(() => {
    let cancelado = false
    fn()
      .then((d) => {
        if (!cancelado) {
          setData(d)
          setError('')
        }
      })
      .catch((e: Error) => {
        if (!cancelado) setError(e.message)
      })
    return () => {
      cancelado = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, ...deps])
  const reload = useCallback(() => setTick((t) => t + 1), [])
  return { data, error, reload }
}

// ---- Avisos ----
type Aviso = { id: number; texto: string; tipo: 'ok' | 'error' }
const ToastCtx = createContext<(texto: string, tipo?: 'ok' | 'error') => void>(() => {})
export const useToast = () => useContext(ToastCtx)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [avisos, setAvisos] = useState<Aviso[]>([])
  const notify = useCallback((texto: string, tipo: 'ok' | 'error' = 'ok') => {
    const id = Date.now() + Math.random()
    setAvisos((a) => [...a, { id, texto, tipo }])
    setTimeout(() => setAvisos((a) => a.filter((x) => x.id !== id)), 4500)
  }, [])
  return (
    <ToastCtx.Provider value={notify}>
      {children}
      <div className="toasts">
        {avisos.map((a) => (
          <div key={a.id} className={`toast ${a.tipo}`}>
            {a.texto}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

/** Ejecuta una acción y avisa el resultado. Devuelve true si salió bien. */
export function useAccion() {
  const notify = useToast()
  return useCallback(
    async (fn: () => Promise<unknown>, okMsg?: string) => {
      try {
        await fn()
        if (okMsg) notify(okMsg)
        return true
      } catch (e) {
        notify((e as Error).message, 'error')
        return false
      }
    },
    [notify],
  )
}

// ---- Componentes ----
export function Badge({ tono, children }: { tono: 'azul' | 'verde' | 'ambar' | 'gris' | 'rojo'; children: ReactNode }) {
  return <span className={`badge ${tono}`}>{children}</span>
}

export function PageHeader({
  titulo,
  subtitulo,
  acciones,
  migas,
}: {
  titulo: ReactNode
  subtitulo?: ReactNode
  acciones?: ReactNode
  migas?: ReactNode
}) {
  return (
    <header className="page-header">
      <div>
        {migas && <div className="migas">{migas}</div>}
        <h1>{titulo}</h1>
        {subtitulo && <p className="sub">{subtitulo}</p>}
      </div>
      {acciones && <div className="acciones-header">{acciones}</div>}
    </header>
  )
}

export function Modal({
  titulo,
  onClose,
  onSubmit,
  submitLabel = 'Guardar',
  children,
}: {
  titulo: string
  onClose: () => void
  onSubmit: () => void | Promise<void>
  submitLabel?: string
  children: ReactNode
}) {
  const [enviando, setEnviando] = useState(false)
  const enviar = async (e: FormEvent) => {
    e.preventDefault()
    setEnviando(true)
    try {
      await onSubmit()
    } finally {
      setEnviando(false)
    }
  }
  return (
    <div className="overlay" onMouseDown={onClose}>
      <form className="modal card" onMouseDown={(e) => e.stopPropagation()} onSubmit={enviar}>
        <h2>{titulo}</h2>
        <div className="modal-body">{children}</div>
        <div className="modal-footer">
          <button type="button" className="btn" onClick={onClose}>
            Cancelar
          </button>
          <button type="submit" className="btn primary" disabled={enviando}>
            {submitLabel}
          </button>
        </div>
      </form>
    </div>
  )
}

export function Campo({
  label,
  ayuda,
  children,
}: {
  label: string
  ayuda?: string
  children: ReactNode
}) {
  return (
    <label className="campo">
      <span>{label}</span>
      {children}
      {ayuda && <small>{ayuda}</small>}
    </label>
  )
}

export function Cargando({ error }: { error: string }) {
  return error ? <div className="aviso-error">{error}</div> : <p className="muted">Cargando…</p>
}
