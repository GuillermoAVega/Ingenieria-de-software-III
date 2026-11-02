# AGENTS.md

Guía de trabajo para agentes que modifiquen este repositorio.

## Estructura

- `Backend/`: FastAPI + SQLAlchemy + Pydantic + SQLite.
- `Frontend/`: React 19 + TypeScript + Vite.
- `openspec/specs/`: especificaciones vigentes.
- `openspec/changes/`: cambios propuestos y archivo histórico.

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
