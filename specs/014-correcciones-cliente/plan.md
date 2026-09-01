# Plan 014 — Correcciones sobre Alta y Listado de Cliente

Plan técnico para implementar `specs/014-correcciones-cliente/spec.md`,
respetando `docs/constitution.md`. No se agregan módulos ni
dependencias nuevas: se ajusta la validación de duplicado de
[[001-alta-cliente]] (reutilizando el patrón ya construido en
[[003-modificacion-cliente]]) y se agrega un texto de ayuda a
[[004-listar-clientes]].

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`repository.py` (extendido)**: agrega
  `active_customer_exists_with_dni(session, dni)`, que verifica si el
  DNI pertenece a un cliente en estado Activo, sin excluir ningún `id`
  (a diferencia de `dni_belongs_to_another_active_customer`, usada por
  la edición, que sí excluye al propio cliente que se está editando —
  en el alta no existe todavía un registro propio que excluir). [Cubre
  RF-1, RF-2]
  No se toca `dni_exists` (usada hoy solo por
  `scripts/seed_clientes_ficticios.py` para evitar reinsertar el mismo
  DNI de prueba sin importar su estado): sigue existiendo tal cual,
  fuera del alcance de esta spec.
- **`routes/clientes.py` (modificado)**: en `alta_cliente`, reemplaza
  la llamada a `repository.dni_exists` por
  `repository.active_customer_exists_with_dni`. [Cubre RF-1, RF-2]

### Frontend (`app/frontend/`)

- **`components/ClienteListado.jsx` (extendido)**: agrega un párrafo de
  ayuda debajo del formulario de búsqueda, con el texto "Podés buscar
  por Nombre, Apellido o DNI." [Cubre RF-3]

## 2. Modelo de la Base de Datos
No se agregan ni modifican tablas ni columnas. Esta spec reutiliza la
tabla `customers` tal cual está definida desde [[001-alta-cliente]]: el
cambio es puramente de qué fila cuenta como "duplicado" (filtrando por
`status == ACTIVE`), no de esquema.

## 3. Contrato de la Interfaz Web

### `POST /clientes` (contrato sin cambios de forma)
- **Método y ruta:** `POST /clientes` (sin cambios).
- **Payload de entrada:** sin cambios (`dni`, `first_name`, `last_name`,
  `email`, `phone`).
- **Respuesta esperada (éxito):** `201 Created` — sin cambios de forma;
  ahora también se alcanza cuando el DNI coincide con un cliente
  Inactivo. [Cubre RF-2]
- **Respuesta esperada (error):** `422 Unprocessable Entity` —
  `{ errors: [{ field: "dni", message: "El cliente ya se encuentra
  registrado" }] }`, ahora solo cuando el DNI coincide con un cliente
  **Activo** (antes: con cualquier estado). [Cubre RF-1]

### Vista "Listar Clientes" (`ClienteListado.jsx`, sin cambios de ruta/flujo)
- **Propósito:** sin cambios; se agrega un texto de ayuda visible bajo
  la barra de búsqueda. [Cubre RF-3]
- **Componentes/estados clave:** el formulario de búsqueda ya existente
  suma un `<p>` informativo inmediatamente debajo, siempre visible
  (no depende de ningún estado de carga o resultado). [Cubre RF-3]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** se agrega una función nueva
   (`active_customer_exists_with_dni`) en vez de modificar `dni_exists`
   para que filtre por Activo.
   **Justificación:** `dni_exists` la sigue usando
   `scripts/seed_clientes_ficticios.py` con su semántica actual ("¿existe
   un cliente con este DNI, sin importar su estado?"), para no reinsertar
   el mismo dato de prueba dos veces; cambiarle el filtrado rompería ese
   uso o exigiría tocar un script fuera del alcance de esta spec.
   **Alternativa descartada:** modificar `dni_exists` para que reciba un
   parámetro `only_active: bool = False` — descartada por ser una
   sobre-generalización para un solo caso de uso adicional; una función
   nueva con un nombre explícito es más clara que un flag booleano.
   *(RF-1, RF-2)*

2. **Decisión Tomada:** `active_customer_exists_with_dni` no recibe un
   `exclude_id`, a diferencia de `dni_belongs_to_another_active_customer`
   (usada por la edición).
   **Justificación:** en el alta todavía no existe ningún registro
   propio del cliente que se está creando; no hay ningún `id` que
   excluir de la comparación, a diferencia de la edición (donde el
   cliente que se edita ya existe y no debe compararse contra sí
   mismo).
   **Alternativa descartada:** reutilizar
   `dni_belongs_to_another_active_customer` pasándole un `exclude_id`
   inexistente (ej. `-1`) — descartada por ser un uso forzado de una
   función pensada para otro caso, menos legible que una función propia
   con un nombre que describe exactamente el alta. *(RF-1)*

3. **Decisión Tomada:** el texto de ayuda de `ClienteListado.jsx` es
   estático (no depende de props, estado ni configuración).
   **Justificación:** RF-3 solo pide comunicar los criterios de
   búsqueda ya fijos (Nombre, Apellido, DNI) definidos desde
   [[004-listar-clientes]] RF-2; no hay nada dinámico que calcular.
   **Alternativa descartada:** generar el texto a partir de una lista de
   campos buscables (pensando en una futura extensión) — descartada por
   diseñar para un requisito que no existe (no se pidió que los campos
   buscables sean configurables).
   *(RF-3)*

## 5. Estrategia de Tests

### Backend — tests unitarios/integración (`repository.py`, SQLite temporal)
- `active_customer_exists_with_dni`: devuelve `True` para un DNI de un
  cliente Activo; devuelve `False` para un DNI que solo pertenece a
  clientes Inactivos; devuelve `False` para un DNI que no existe.
  [Cubre RF-1, RF-2]

### Backend — tests de integración (`routes/clientes.py`, `TestClient`)
- `POST /clientes` con un DNI que pertenece a un cliente Activo sigue
  devolviendo 422 con el mensaje de duplicado. [Cubre RF-1]
- `POST /clientes` con un DNI que pertenece únicamente a un cliente
  Inactivo devuelve 201, y el cliente Inactivo original queda sin
  modificar (mismo nombre/estado que antes del alta). [Cubre RF-2]
- Tras ese alta, existen dos clientes distintos (`id` distintos) con el
  mismo valor de DNI, uno Activo y uno Inactivo. [Cubre RF-2]

### Frontend — Vitest + RTL sobre `ClienteListado.jsx`
- El texto "Podés buscar por Nombre, Apellido o DNI." está presente al
  renderizar el componente, sin necesidad de interactuar con el
  formulario. [Cubre RF-3]

### Verificación de tipado
`npm run typecheck` como parte del pipeline de cada tarea.

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** sin dependencias nuevas.
- **Regla 2 (spec antes que código):** parte de
  `specs/014-correcciones-cliente/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** la regla de duplicado
  sigue viviendo en `repository.py`, testeable sin HTTP ni React.
- **Regla 4 (tests obligatorios):** la estrategia cubre las 3 RF de la
  spec.
- **Regla 5 (persistencia única):** `active_customer_exists_with_dni`
  lee exclusivamente de `database.py`/la tabla `customers`.
- **Regla 6 (idioma consistente):** identificador en inglés
  (`active_customer_exists_with_dni`); mensaje y texto de ayuda en
  español.
