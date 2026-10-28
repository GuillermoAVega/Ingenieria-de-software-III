// ui.jsx — componentes React finos sobre ui.css.
// Regla: en las pantallas se usan estos componentes (o las clases de ui.css), nunca estilos propios.
import { useId, cloneElement, isValidElement } from 'react';

const cx = (...c) => c.filter(Boolean).join(' ');

/* ---------- Botón ---------- */
// variant: primary | secondary | ghost | danger | danger-ghost   size: md | sm
export function Button({ variant = 'secondary', size = 'md', block, className, type = 'button', ...props }) {
  return (
    <button
      type={type}
      className={cx('btn', `btn-${variant}`, size === 'sm' && 'btn-sm', block && 'btn-block', className)}
      {...props}
    />
  );
}

/* ---------- Card ---------- */
export function Card({ title, subtitle, actions, footer, flush, children, className, ...props }) {
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
  );
}

/* ---------- Badge ---------- */
// tone: neutral | success | warning | danger | info
export function Badge({ tone = 'neutral', children }) {
  return <span className={cx('badge', tone !== 'neutral' && `badge-${tone}`)}>{children}</span>;
}

/* ---------- Formularios ---------- */
// <Field label="Nombre" required error={errors.nombre} hint="..."><Input {...register('nombre')} /></Field>
export function Field({ label, required, hint, error, children, className }) {
  const id = useId();
  const control = isValidElement(children)
    ? cloneElement(children, { id, 'aria-invalid': !!error || undefined, invalid: !!error, ...children.props })
    : children;
  return (
    <div className={cx('field', className)}>
      {label && (
        <label className="label" htmlFor={id}>
          {label} {required && <span className="req">*</span>}
        </label>
      )}
      {control}
      {error ? <span className="error-text">{error}</span> : hint && <span className="hint">{hint}</span>}
    </div>
  );
}
export const Input = ({ invalid, className, ...p }) => <input className={cx('input', invalid && 'is-invalid', className)} {...p} />;
export const Textarea = ({ invalid, className, ...p }) => <textarea className={cx('textarea', invalid && 'is-invalid', className)} {...p} />;
export const Select = ({ invalid, className, children, ...p }) => (
  <select className={cx('select', invalid && 'is-invalid', className)} {...p}>{children}</select>
);
export const Check = ({ children, ...p }) => <label className="check"><input type="checkbox" {...p} /> {children}</label>;
export const Switch = ({ children, ...p }) => <label className="switch"><input type="checkbox" {...p} /> {children}</label>;

/* ---------- Estructura de pantalla ---------- */
export function PageHeader({ title, subtitle, actions, breadcrumb }) {
  return (
    <header className="page-header">
      <div>
        {breadcrumb}
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-sub">{subtitle}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  );
}

// nav = [{ label: 'Operación', items: [{ text, href, active }] }]
export function AppShell({ nav, user, children }) {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">R</span>Restó</div>
        <nav className="nav" aria-label="Principal">
          {nav.map((g) => (
            <div key={g.label} style={{ display: 'contents' }}>
              <div className="nav-label">{g.label}</div>
              {g.items.map((i) => (
                <a key={i.href} href={i.href} className={cx('nav-link', i.active && 'is-active')}>{i.text}</a>
              ))}
            </div>
          ))}
        </nav>
        {user && (
          <div className="user">
            <span className="avatar">{user.initials}</span>
            <div><div className="cell-main">{user.name}</div><div className="cell-sub">{user.role}</div></div>
          </div>
        )}
      </aside>
      <main className="main"><div className="content">{children}</div></main>
    </div>
  );
}

/* ---------- Tabla ---------- */
// columns = [{ key, header, num?, render?(row) }]   actions?(row) => nodes
export function DataTable({ columns, rows, rowKey = 'id', actions, empty }) {
  if (!rows.length) return empty ?? <div className="empty"><span className="empty-title">Sin resultados</span></div>;
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((c) => <th key={c.key} className={c.num ? 'num' : undefined}>{c.header}</th>)}
            {actions && <th className="col-actions">Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r[rowKey]}>
              {columns.map((c) => <td key={c.key} className={c.num ? 'num' : undefined}>{c.render ? c.render(r) : r[c.key]}</td>)}
              {actions && <td className="col-actions">{actions(r)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------- Modal de confirmación ---------- */
export function ConfirmDialog({ open, title, children, confirmLabel = 'Eliminar', danger = true, onConfirm, onCancel }) {
  if (!open) return null;
  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">{title}</div>
        <div className="modal-body">{children}</div>
        <div className="modal-footer">
          <Button onClick={onCancel}>Cancelar</Button>
          <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  );
}

export const EmptyState = ({ title, children, action }) => (
  <div className="empty"><span className="empty-title">{title}</span>{children && <span>{children}</span>}{action}</div>
);
