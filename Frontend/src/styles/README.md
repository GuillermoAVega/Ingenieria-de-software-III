# UI kit — Sistema de gestión de restaurante

Cuatro archivos, para copiar tal cual en `frontend/src/styles/` (React + Vite):

| Archivo | Para qué |
|---|---|
| `ui.css` | Tokens (colores, radios, sombras) y todas las clases de componentes. Sin dependencias. |
| `ui.jsx` | Componentes React finos sobre esas clases: `Button`, `Card`, `Field`, `Input`, `Select`, `Badge`, `DataTable`, `ConfirmDialog`, `PageHeader`, `AppShell`… |
| `tailwind-theme.css` | Opcional (Tailwind v4): expone los tokens como `bg-surface`, `text-muted`, `border-line`, etc. |
| `README.md` | Esta guía. |

## Instalación

**Sin Tailwind:** en `main.jsx` → `import './styles/ui.css'`.

**Con Tailwind v4:** en `index.css` → `@import "./styles/tailwind-theme.css";` (ya incluye Tailwind y `ui.css`).

## Reglas del equipo

1. No se escriben colores, radios, sombras ni fuentes propios. Todo sale de las variables `--c-*` / `--radius-*` / `--shadow-*`.
2. Cada pantalla ABM arma su UI con los componentes de `ui.jsx` o con las clases de `ui.css`.
3. Si falta algo, se agrega a `ui.css` (en un PR chico) y se avisa; no se resuelve localmente en la pantalla.
4. Tailwind sirve para espaciado y layout puntual (`flex`, `gap-4`, `mt-6`), no para recolorear componentes.

## Plantilla de un ABM (listado)

```jsx
<PageHeader title="Mozos" subtitle="Alta, baja y modificación"
  actions={<Button variant="primary">Nuevo mozo</Button>} />

<Card flush>
  <div className="toolbar"><input className="input" placeholder="Buscar" /></div>
  <DataTable
    columns={[{ key: 'nombre', header: 'Nombre' }, { key: 'nroLegajo', header: 'Legajo' }]}
    rows={mozos}
    actions={(m) => (<>
      <Button variant="ghost" size="sm">Editar</Button>
      <Button variant="danger-ghost" size="sm">Eliminar</Button>
    </>)}
  />
</Card>
```

## Plantilla de un formulario

```jsx
<form className="card">
  <div className="card-body form-grid">
    <Field label="Nombre" required error={errors.nombre}><Input /></Field>
    <Field label="Sección" required><Select>…</Select></Field>
  </div>
  <div className="card-footer">
    <Button>Cancelar</Button>
    <Button variant="primary" type="submit">Guardar</Button>
  </div>
</form>
```

## Cheat-sheet de clases

- **Layout:** `.app` `.sidebar` `.main` `.content` `.page-header` `.layout-aside` `.grid-auto` `.grid-2` `.stack` `.row`
- **Cards:** `.card` `.card-header` `.card-body` `.card-footer` `.stat`
- **Botones:** `.btn` + `.btn-primary | -secondary | -ghost | -danger | -danger-ghost` + `.btn-sm`
- **Formularios:** `.field` `.label` `.input` `.select` `.textarea` `.check` `.switch` `.input-group` `.dropzone` `.is-invalid` `.hint` `.error-text`
- **Datos:** `.table` `.toolbar` `.tabs` `.tab` `.pagination` `.badge` `.badge-success | -warning | -danger | -info`
- **Feedback:** `.alert` `.empty` `.modal-backdrop` `.modal`
- **Dominio:** `.mesa` (`.is-busy`, `.is-reserved`) `.bar-row` `.kv`

## Tailwind v3

Si el proyecto usa v3, mapear en `tailwind.config.js`:

```js
theme: { extend: { colors: {
  surface: 'var(--c-surface)', bg: 'var(--c-bg)', line: 'var(--c-border)',
  ink: 'var(--c-text)', muted: 'var(--c-text-3)', accent: 'var(--c-accent)',
} } }
```
