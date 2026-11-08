# AGENTS.md — Frontend

Guía para agentes que modifiquen `Frontend/`.

- Stack: React 19 + TypeScript + Vite.
- Código en `Frontend/src/`.
- Los mensajes visibles para el usuario se mantienen en español; los identificadores de código en inglés.

## Frontend: estado y hooks

### Un único objeto de estado por componente o hook

No se deben crear múltiples `useState` para cada campo del mismo formulario o pantalla. El estado relacionado debe agruparse en un único objeto tipado.

Incorrecto:

```tsx
const [nombre, setNombre] = useState('')
const [precio, setPrecio] = useState('')
const [loading, setLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
```

Correcto:

```tsx
type ProductFormState = {
  nombre: string
  precio: string
  loading: boolean
  error: string | null
}

const [state, setState] = useState<ProductFormState>(initialState)
```

Las actualizaciones deben ser inmutables y usar la forma funcional cuando dependan del estado anterior:

```tsx
setState((previous) => ({ ...previous, [field]: value }))
```

### Separar la lógica de la pantalla mediante hooks

La lógica de un formulario o pantalla no debe vivir dentro del componente de renderizado. Debe extraerse a un hook propio de la feature, por ejemplo:

- `Frontend/src/features/products/useProductForm.ts`
- `Frontend/src/features/sections/useSectionForm.ts`

El hook es responsable de:

- Inicializar y mantener el estado del formulario.
- Cargar datos desde la API.
- Validar y transformar los datos antes de enviarlos.
- Ejecutar el alta, la modificación o el borrado.
- Manejar estados de carga, guardado y errores.
- Exponer acciones estables para la pantalla: `updateField`, `submit`, etc.

El componente debe limitarse a:

- Renderizar el formulario.
- Conectar los eventos a las acciones del hook.
- Mostrar los estados y errores que expone el hook.

Ejemplo de uso esperado:

```tsx
function ProductForm({ id }: { id?: string }) {
  const { state, isEditing, updateField, submit } = useProductForm(id)

  return (
    <form onSubmit={submit}>
      <Input
        value={state.nombre}
        onChange={(event) => updateField('nombre', event.target.value)}
      />
    </form>
  )
}
```

### Reglas adicionales

- No llamar a `fetch` directamente desde componentes o páginas. Usar `apiFetch` y las funciones de API de cada feature.
- No duplicar lógica de carga o envío entre pantallas; si dos pantallas comparten comportamiento, extraer un hook.
- No usar `useEffect` para inicializar estado derivado de props. Usar inicializadores de `useState` o un componente interno con `key` cuando corresponda.
- Evitar `setState` síncrono dentro del cuerpo de un `useEffect`; las cargas asíncronas deben encapsularse en una función async.
- Nombrar los hooks con el prefijo `use` y ubicarlos junto a la feature que los consume.
- Mantener los mensajes de interfaz en español y los identificadores de código en inglés.

## Frontend: componentes

### Un componente por archivo

No definir varios componentes en el mismo archivo. Cada componente debe vivir en su propio archivo con el mismo nombre del componente y usar `export` nombrado.

Incorrecto: acumular `MenuItemRow`, `MenuSectionFrame`, `MenuCover`, etc. dentro de `MenuViewPage.tsx`.

Correcto:

```tsx
// Frontend/src/features/menu-view/components/MenuItemRow.tsx
export function MenuItemRow({ item }: { item: MenuViewItem }) {
  return <li className="menu-view-item">{item.nombre}</li>
}
```

### Subcarpeta `components`

Cuando una feature tenga varios componentes reutilizables o subcomponentes, ubicarlos en `Frontend/src/features/<feature>/components/`. El archivo de la página se limita a componer la pantalla y conectar los hooks; el markup de bloques, tarjetas, filas, carátulas e impresión va en componentes separados.

Estructura esperada:

```text
Frontend/src/features/menu-view/
  MenuViewPage.tsx      # solo compone la pantalla
  useMenuView.ts
  useMenuViewPrint.ts
  pagination.ts
  components/
    MenuCover.tsx
    MenuItemRow.tsx
    MenuSectionFrame.tsx
    PrintablePageView.tsx
    PrintablePages.tsx
```

Reglas adicionales:

- Los componentes de `components/` reciben datos por props; no cargan datos ni llaman a la API.
- Exportar funciones con nombre (`export function`) y, si hace falta, exportar también el tipo de props.
- No crear archivos "barrel" (`index.ts`) salvo que exista una razón concreta; importar cada componente desde su archivo.

## Frontend: comandos

Ejecutar desde `Frontend/`:

- Build y verificación de tipos: `npm run build`.
- Lint de una ruta: `npx eslint src/features/<feature>`.
