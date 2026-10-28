// ui.tsx — componentes React finos sobre ui.css.
// Regla: en las pantallas se usan estos componentes (o las clases de ui.css), nunca estilos propios.
import { Fragment, cloneElement, isValidElement, useId, useState } from 'react'
import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
  InputHTMLAttributes,
  Key,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from 'react'

const cx = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ')

/* ---------- Botón ---------- */
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'danger-ghost'
export type ButtonSize = 'md' | 'sm'

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant
  size?: ButtonSize
  block?: boolean
}

export function Button({
  variant = 'secondary',
  size = 'md',
  block = false,
  className,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cx('btn', `btn-${variant}`, size === 'sm' && 'btn-sm', block && 'btn-block', className)}
      {...props}
    />
  )
}

/* ---------- Card ---------- */
export type CardProps = Omit<HTMLAttributes<HTMLElement>, 'title'> & {
  title?: ReactNode
  subtitle?: ReactNode
  actions?: ReactNode
  footer?: ReactNode
  flush?: boolean
}

export function Card({
  title,
  subtitle,
  actions,
  footer,
  flush = false,
  children,
  className,
  ...props
}: CardProps) {
  return (
    <section className={cx('card', className)} {...props}>
      {(title || actions) && (
        <div className="card-header">
          <div>
            {title && <h2 className="card-title">{title}</h2>}
            {subtitle && <p className="card-sub">{subtitle}</p>}
          </div>
          {actions}
        </div>
      )}
      <div className={flush ? 'card-flush' : 'card-body'}>{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </section>
  )
}

/* ---------- Badge ---------- */
export type BadgeTone = 'neutral' | 'success' | 'warning' | 'danger' | 'info'

export function Badge({ tone = 'neutral', children }: { tone?: BadgeTone; children: ReactNode }) {
  return <span className={cx('badge', tone !== 'neutral' && `badge-${tone}`)}>{children}</span>
}

/* ---------- Formularios ---------- */
export type FieldProps = {
  label?: ReactNode
  required?: boolean
  hint?: ReactNode
  error?: ReactNode
  children?: ReactNode
  className?: string
}

export function Field({ label, required = false, hint, error, children, className }: FieldProps) {
  const id = useId()
  const isFormControl =
    isValidElement(children) &&
    (children.type === Input ||
      children.type === Textarea ||
      children.type === Select ||
      children.type === InputGroup)
  const control = isValidElement<Record<string, unknown>>(children)
    ? cloneElement(children, {
        id,
        'aria-invalid': error ? true : undefined,
        ...(isFormControl ? { invalid: Boolean(error) } : {}),
      })
    : children

  return (
    <div className={cx('field', className)}>
      {label && (
        <label className="label" htmlFor={id}>
          {label} {required && <span className="req">*</span>}
        </label>
      )}
      {control}
      {error ? <span className="error-text">{error}</span> : hint ? <span className="hint">{hint}</span> : null}
    </div>
  )
}

export type InputProps = InputHTMLAttributes<HTMLInputElement> & { invalid?: boolean }

export function Input({ invalid = false, className, ...props }: InputProps) {
  return <input className={cx('input', invalid && 'is-invalid', className)} {...props} />
}

export type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & { invalid?: boolean }

export function Textarea({ invalid = false, className, ...props }: TextareaProps) {
  return <textarea className={cx('textarea', invalid && 'is-invalid', className)} {...props} />
}

export type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & { invalid?: boolean }

export function Select({ invalid = false, className, children, ...props }: SelectProps) {
  return (
    <select className={cx('select', invalid && 'is-invalid', className)} {...props}>
      {children}
    </select>
  )
}

export type InputGroupProps = {
  id?: string
  invalid?: boolean
  prefix?: ReactNode
  children: ReactNode
}

export function InputGroup({ id, invalid = false, prefix, children }: InputGroupProps) {
  const control = isValidElement<Record<string, unknown>>(children)
    ? cloneElement(children, {
        id,
        'aria-invalid': invalid ? true : undefined,
        invalid,
      })
    : children

  return (
    <div className="input-group">
      {prefix !== undefined && <span className="input-prefix">{prefix}</span>}
      {control}
    </div>
  )
}

export function Check({ children, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="check">
      <input type="checkbox" {...props} /> {children}
    </label>
  )
}

export function Switch({ children, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="switch">
      <input type="checkbox" {...props} /> {children}
    </label>
  )
}

/* ---------- Estructura de pantalla ---------- */
export type PageHeaderProps = {
  title: ReactNode
  subtitle?: ReactNode
  actions?: ReactNode
  breadcrumb?: ReactNode
}

export function PageHeader({ title, subtitle, actions, breadcrumb }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div>
        {breadcrumb}
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-sub">{subtitle}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  )
}

export type BreadcrumbItem = {
  label: string
  href?: string
}

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav className="breadcrumb" aria-label="Ruta de navegación">
      {items.map((item, index) => (
        <Fragment key={`${item.label}-${index}`}>
          {index > 0 && <span aria-hidden="true">/</span>}
          {item.href ? <a href={item.href}>{item.label}</a> : <span>{item.label}</span>}
        </Fragment>
      ))}
    </nav>
  )
}

export type NavItem = {
  text: string
  href: string
  active?: boolean
}

export type NavGroup = {
  label: string
  items: NavItem[]
}

export type AppShellUser = {
  name: string
  role: string
  initials: string
}

export function AppShell({
  nav,
  user,
  children,
}: {
  nav: NavGroup[]
  user?: AppShellUser
  children: ReactNode
}) {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">R</span>Restó
        </div>
        <nav className="nav" aria-label="Principal">
          {nav.map((group) => (
            <Fragment key={group.label}>
              <div className="nav-label">{group.label}</div>
              {group.items.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  className={cx('nav-link', item.active && 'is-active')}
                  aria-current={item.active ? 'page' : undefined}
                >
                  {item.text}
                </a>
              ))}
            </Fragment>
          ))}
        </nav>
        {user && (
          <div className="user">
            <span className="avatar">{user.initials}</span>
            <div>
              <div className="cell-main">{user.name}</div>
              <div className="cell-sub">{user.role}</div>
            </div>
          </div>
        )}
      </aside>
      <main className="main">
        <div className="content">{children}</div>
      </main>
    </div>
  )
}

/* ---------- Tabla ---------- */
export type DataTableColumn<T> = {
  key: string
  header: ReactNode
  num?: boolean
  render?: (row: T) => ReactNode
}

export type DataTableProps<T> = {
  columns: DataTableColumn<T>[]
  rows: T[]
  rowKey?: keyof T | ((row: T) => Key)
  actions?: (row: T) => ReactNode
  empty?: ReactNode
}

function getRowKey<T>(row: T, rowKey: DataTableProps<T>['rowKey'], index: number): Key {
  if (typeof rowKey === 'function') return rowKey(row)
  if (rowKey) {
    const value = row[rowKey]
    if (typeof value === 'string' || typeof value === 'number') return value
  }
  const fallback = (row as unknown as { id?: unknown }).id
  if (typeof fallback === 'string' || typeof fallback === 'number') return fallback
  return index
}

function renderDefault<T>(row: T, key: string): ReactNode {
  const value = (row as unknown as Record<string, unknown>)[key]
  return typeof value === 'string' || typeof value === 'number' ? value : null
}

export function DataTable<T>({ columns, rows, rowKey, actions, empty }: DataTableProps<T>) {
  if (!rows.length) {
    return empty ?? <div className="empty"><span className="empty-title">Sin resultados</span></div>
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} className={column.num ? 'num' : undefined}>
                {column.header}
              </th>
            ))}
            {actions && <th className="col-actions">Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={getRowKey(row, rowKey, index)}>
              {columns.map((column) => (
                <td key={column.key} className={column.num ? 'num' : undefined}>
                  {column.render ? column.render(row) : renderDefault(row, column.key)}
                </td>
              ))}
              {actions && <td className="col-actions">{actions(row)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/* ---------- Tabs, toolbar y paginación ---------- */
export type TabItem = {
  id: string
  label: string
  count?: number
}

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: TabItem[]
  active: string
  onChange: (id: string) => void
}) {
  return (
    <div className="tabs" role="tablist">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={active === tab.id}
          className={cx('tab', active === tab.id && 'is-active')}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
          {tab.count !== undefined && <span className="tab-count">{tab.count}</span>}
        </button>
      ))}
    </div>
  )
}

export function Toolbar({ children }: { children?: ReactNode }) {
  return <div className="toolbar">{children}</div>
}

export function ToolbarSpacer() {
  return <span className="toolbar-spacer" />
}

export type PaginationProps = {
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
  label?: string
}

export function Pagination({ page, pageSize, total, onPageChange, label }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  return (
    <div className="pagination">
      <span>{label ?? `Página ${page} de ${totalPages} · ${total} registros`}</span>
      <div className="pager">
        <Button size="sm" onClick={() => onPageChange(page - 1)} disabled={page <= 1}>
          Anterior
        </Button>
        <Button size="sm" onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}>
          Siguiente
        </Button>
      </div>
    </div>
  )
}

/* ---------- Estados y métricas ---------- */
export function Stat({ label, value, hint }: { label: ReactNode; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className="stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
      {hint && <span className="stat-hint">{hint}</span>}
    </div>
  )
}

export type AlertTone = 'info' | 'success' | 'warning' | 'danger'

export function Alert({ tone = 'info', title, children }: { tone?: AlertTone; title?: ReactNode; children?: ReactNode }) {
  return (
    <div className={cx('alert', tone !== 'info' && `alert-${tone}`)} role="status">
      {title && <div className="alert-title">{title}</div>}
      {children}
    </div>
  )
}

export function EmptyState({ title, children, action }: { title: ReactNode; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="empty">
      <span className="empty-title">{title}</span>
      {children && <span>{children}</span>}
      {action}
    </div>
  )
}

/* ---------- Modal ---------- */
export type ConfirmDialogProps = {
  open: boolean
  title: ReactNode
  children?: ReactNode
  confirmLabel?: string
  danger?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  title,
  children,
  confirmLabel = 'Eliminar',
  danger = true,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null
  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={typeof title === 'string' ? title : 'Confirmar acción'}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">{title}</div>
        <div className="modal-body">{children}</div>
        <div className="modal-footer">
          <Button onClick={onCancel}>Cancelar</Button>
          <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  )
}

export type DeleteButtonProps = {
  label?: string
  title: ReactNode
  confirmLabel?: string
  size?: ButtonSize
  children?: ReactNode
  onConfirm: () => void
}

export function DeleteButton({
  label = 'Eliminar',
  title,
  confirmLabel = 'Eliminar',
  size = 'sm',
  children,
  onConfirm,
}: DeleteButtonProps) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button variant="danger-ghost" size={size} onClick={() => setOpen(true)}>
        {label}
      </Button>
      <ConfirmDialog
        open={open}
        title={title}
        confirmLabel={confirmLabel}
        onCancel={() => setOpen(false)}
        onConfirm={() => {
          onConfirm()
          setOpen(false)
        }}
      >
        {children}
      </ConfirmDialog>
    </>
  )
}

export type ModalProps = {
  open: boolean
  title: ReactNode
  children?: ReactNode
  footer?: ReactNode
  onClose: () => void
}

export function Modal({ open, title, children, footer, onClose }: ModalProps) {
  if (!open) return null
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={typeof title === 'string' ? title : 'Diálogo'}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">{title}</div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  )
}

/* ---------- Componentes de dominio ---------- */
export function Dropzone({ title, hint, action }: { title: ReactNode; hint?: ReactNode; action?: ReactNode }) {
  return (
    <div className="dropzone">
      <span className="cell-main">{title}</span>
      {hint && <span className="hint">{hint}</span>}
      {action}
    </div>
  )
}

export function KeyValue({ label, value, total = false }: { label: ReactNode; value: ReactNode; total?: boolean }) {
  return (
    <div className={cx('kv', total && 'kv-total')}>
      <span>{label}</span>
      <span>{value}</span>
    </div>
  )
}

export function BarRow({ label, value, max }: { label: string; value: number; max: number }) {
  const percent = max > 0 ? Math.round((value / max) * 100) : 0
  return (
    <div className="bar-row">
      <span>{label}</span>
      <div className="bar">
        <span style={{ width: `${percent}%` }} />
      </div>
      <span className="num">{value}</span>
    </div>
  )
}
