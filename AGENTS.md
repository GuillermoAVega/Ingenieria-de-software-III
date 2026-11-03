# AGENTS.md

Guía de trabajo para agentes que modifiquen este repositorio.

## Estructura

- `Backend/`: FastAPI + SQLAlchemy + Pydantic + SQLite.
- `Frontend/`: React 19 + TypeScript + Vite.
- `openspec/specs/`: especificaciones vigentes.
- `openspec/changes/`: cambios propuestos y archivo histórico.

## Modularidad y responsabilidad única

Todo cambio nuevo y toda refactorización debe mantener el código modularizado, con la menor cantidad de código necesaria para resolver el problema.

### Frontend

- Las páginas deben coordinar la pantalla y renderizar; no deben contener reglas de negocio, llamadas HTTP ni transformaciones complejas.
- La lógica de estado, carga, validación y envío debe vivir en hooks propios de la feature.
- Las llamadas HTTP deben vivir en `api.ts` de la feature y usar `apiFetch` o el cliente compartido.
- Los componentes visuales reutilizables deben extraerse a archivos propios dentro de la feature o de `ui` cuando sean realmente compartidos.
- Los tipos y estados deben declararse junto a la feature que los usa; no duplicar tipos ni respuestas de API.
- Las funciones de formato, selección y transformación reutilizables deben extraerse a módulos pequeños, puros y testeables.
- No agregar componentes, hooks, estados, props, estilos ni funciones que no sean necesarios para el comportamiento solicitado.
- No mantener código de demostración, imports, variables ni ramas sin uso en funcionalidades reales.
- Una refactorización debe conservar el comportamiento existente; los cambios funcionales deben hacerse en un commit separado.

### Backend

- Los routers deben limitarse a recibir la petición, validar dependencias y delegar en servicios.
- Las reglas de negocio deben vivir en servicios del dominio y no repetirse entre routers.
- Los schemas definen contratos de entrada y salida; los modelos definen persistencia y relaciones.
- Las consultas reutilizables deben extraerse a servicios o repositorios pequeños cuando eviten duplicación.
- Cada módulo debe depender de contratos claros y evitar importar detalles internos de otra feature sin necesidad.
- No crear funciones genéricas o abstracciones prematuras: extraer solo cuando exista responsabilidad duplicada o una unidad de comportamiento clara.

### Forma de refactorizar

- Refactorizar por feature y en pasos pequeños.
- Antes de mover código, identificar qué responsabilidad se separa y mantener las interfaces públicas estables.
- Verificar cada paso con los tests correspondientes y, en Frontend, con `npx tsc -b --pretty false`.
- Revisar el diff para asegurar que el commit incluya solo la refactorización prevista.

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
