# Plan 004 — Listar Clientes

Plan técnico para implementar `specs/004-listar-clientes/spec.md`,
respetando `docs/constitution.md` y reutilizando lo ya construido en
[[001-alta-cliente]], [[002-baja-cliente]] y [[003-modificacion-cliente]]
(`Customer`, `_serialize_customer`, `clientesApi.js`). Este documento no
contiene código: describe estructura, decisiones y estrategia de
verificación.

## 1. Estructura de Módulos

### Backend (`app/backend/`)

- **`core.py` (extendido)**: agrega `normalize_search_text` (minúsculas +
  sin tildes, para comparar Nombre/Apellido de forma insensible) y
  `matches_search` (decide si un cliente coincide con un criterio ya
  normalizado, comparando contra Nombre, Apellido y DNI). Son funciones
  puras, sin dependencia de la base de datos ni de FastAPI. [Cubre RF-2,
  RF-3, RF-4]
- **`repository.py` (extendido)**: agrega `list_customers(session, query,
  page, page_size=20)`, que trae todos los clientes (Activos e Inactivos,
  ordenados por apellido y nombre), aplica `core.matches_search` cuando hay
  criterio, y devuelve la porción de esa página junto con si existe una
  página siguiente. Es la única función que lee la tabla `customers` para
  esta feature. [Cubre RF-1, RF-2, RF-6, RF-8]
- **`routes/clientes.py` (extendido)**: agrega `GET /clientes` (distinto de
  `GET /clientes/{dni}`, ya existente para la búsqueda puntual de
  [[002-baja-cliente]]), que orquesta: recorta y normaliza el parámetro
  `q`, llama a `repository.list_customers`, y arma la respuesta paginada
  reutilizando `_serialize_customer`. [Cubre RF-1 a RF-8]

### Frontend (`app/frontend/`)

- **`api/clientesApi.js` (extendido)**: agrega `listarClientes({ q, page
  })`, que llama a `GET /clientes` y devuelve `{ customers, page, hasNext
  }`. No distingue éxito/error como las demás funciones porque este
  endpoint no tiene un camino de "solicitud inválida" alcanzable desde la
  UI (la página siempre es un entero ≥ 1 controlado por los propios
  botones de paginación). [Cubre RF-1, RF-2, RF-8]
- **`components/ClienteListado.jsx` (nuevo)**: input de búsqueda (con
  debounce simple o disparo por submit, ver Decisión 4), tabla de
  resultados (DNI, Nombre, Apellido, Estado), mensaje de "no se encontraron
  resultados" cuando la lista viene vacía, y controles
  Anterior/Siguiente. Al montarse, pide la página 1 sin filtro (vista
  inicial). [Cubre RF-1 a RF-8]
- **`App.jsx` (extendido)**: agrega la cuarta pestaña "Listar Clientes".
  [Estructural, sin RF directo]

## 2. Modelo de la Base de Datos

No se agregan tablas ni columnas nuevas. Esta feature es de solo lectura
sobre la tabla `customers` ya definida en `models.py`
([[001-alta-cliente]]):

| Columna | Tipo | Uso en esta feature |
|---|---|---|
| `dni` | Integer, indexado | Se compara como texto (`str(dni)`) contra el criterio de búsqueda. [Cubre RF-2, RF-3] |
| `first_name`, `last_name` | String | Se comparan normalizados (sin mayúsculas ni tildes) contra el criterio. [Cubre RF-2, RF-3, RF-4] |
| `status` | Enum (`Activo`/`Inactivo`) | Se muestra en cada fila; no se usa como filtro (RF-6 exige incluir ambos estados siempre). [Cubre RF-1, RF-6] |

El filtrado por Nombre/Apellido se resuelve en Python, no con `LIKE` de
SQL (ver Decisión Técnica 2), por lo que no se agrega ningún índice ni
columna auxiliar de texto normalizado.

## 3. Contrato de la Interfaz Web

### Endpoint: `GET /clientes`

- **Método y ruta:** `GET /clientes?q=<texto opcional>&page=<entero, default 1>`
- **Payload de entrada:** query params `q` (string, opcional) y `page`
  (entero ≥ 1, opcional, default 1).
- **Respuesta esperada (éxito):** `200 OK`
  ```json
  {
    "customers": [
      { "dni": 30111222, "first_name": "Juan", "last_name": "Perez",
        "email": "juan@dominio.com", "phone": "11-4444-5555", "status": "Activo" }
    ],
    "page": 1,
    "has_next": false
  }
  ```
  Un `q` sin coincidencias devuelve `"customers": []` con `200 OK` (RF-5 se
  resuelve en el Frontend a partir de un arreglo vacío, no con un código de
  error). [Cubre RF-1, RF-2, RF-3, RF-4, RF-5, RF-6, RF-8]
- **Respuesta esperada (error):** `422 Unprocessable Entity` (generado por
  FastAPI) únicamente si `page` no es un entero ≥ 1; no alcanzable desde la
  UI en uso normal, ya que los botones de paginación nunca envían un valor
  inválido.

### Vista: pestaña "Listar Clientes" (`ClienteListado.jsx`)

- **Ruta/URL:** no aplica (SPA de una sola página con pestañas, igual que
  Alta/Baja/Edición).
- **Propósito:** consultar y filtrar la nómina de clientes por Nombre,
  Apellido o DNI, viendo su estado. [Cubre HU-CLI-04]
- **Componentes/estados clave:**
  - Campo de búsqueda único (`q`).
  - Tabla de resultados con columnas DNI / Nombre / Apellido / Estado.
  - Estado "sin resultados": mensaje en vez de tabla vacía. [Cubre RF-5]
  - Controles "Anterior" / "Siguiente", deshabilitados cuando no hay página
    previa o siguiente. [Cubre RF-8]
  - Al modificar el campo de búsqueda, la página vuelve a 1. [Cubre RF-7,
    RF-8]

## 4. Decisiones Técnicas

1. **Decisión Tomada:** filtrar y paginar en Python (dentro de
   `repository.list_customers`), trayendo todos los clientes de la tabla y
   aplicando `core.matches_search`/`slice` en memoria, en vez de traducir
   el filtro a `LIKE`/`ORDER BY`/`LIMIT` de SQL.
   **Justificación:** RF-4 exige insensibilidad a tildes, algo que SQLite
   no resuelve de forma nativa con `LIKE` (su `COLLATE NOCASE` ignora
   mayúsculas pero no acentos); resolverlo en SQL requeriría una extensión
   o columnas de texto normalizado adicionales, lo cual la constitución
   (regla 1) exige justificar y no está justificado para el volumen de
   datos de este proyecto.
   **Alternativa descartada:** agregar una extensión SQLite de comparación
   sin acentos, o columnas `first_name_normalized`/`last_name_normalized`
   mantenidas en cada alta/edición — descartada por la complejidad y el
   riesgo de que esas columnas queden desincronizadas si se escribe un
   cliente sin pasar por `core.normalize_search_text`. *(RF-2, RF-3, RF-4)*

2. **Decisión Tomada:** `core.normalize_search_text` y `core.matches_search`
   son funciones puras en `core.py`, separadas de `repository.py`.
   **Justificación:** regla 3 de la constitución — la regla de negocio de
   "qué cuenta como coincidencia" debe ser testeable sin base de datos,
   igual que las validaciones de formato de [[001-alta-cliente]].
   **Alternativa descartada:** escribir la comparación directamente dentro
   de `list_customers` — descartada porque mezclaría la regla de negocio
   con el acceso a datos, dificultando probarla de forma aislada. *(RF-2,
   RF-3, RF-4)*

3. **Decisión Tomada:** el endpoint no distingue entre Activos e Inactivos
   a nivel de query — siempre trae ambos y dejas que RF-6 se cumpla por
   diseño, sin un parámetro `status` opcional.
   **Justificación:** la spec no pide filtrar por estado, solo mostrarlo;
   agregar un parámetro no usado sería anticipar un requisito que no existe
   (regla de "no diseñar para hipotéticos" del proyecto).
   **Alternativa descartada:** exponer `?status=Activo` opcional desde ya —
   descartada por no estar pedida por ningún RF de esta spec. *(RF-6)*

4. **Decisión Tomada:** el filtro se dispara al enviar el formulario de
   búsqueda (submit), no en cada tecla (sin debounce ni petición por cada
   carácter).
   **Justificación:** mantiene el mismo patrón de interacción que
   `ClienteBajaForm.jsx` y `ClienteEdicionForm.jsx` (buscar por DNI con un
   botón "Buscar"), en vez de introducir un mecanismo de debounce nuevo sin
   pedido explícito en la spec.
   **Alternativa descartada:** disparar la búsqueda en cada tecla con
   debounce — descartada por no estar pedida y por agregar complejidad
   (temporizadores, cancelación de pedidos en vuelo) no justificada. *(RF-2)*

5. **Decisión Tomada:** no se crea un módulo puro adicional tipo
   `clienteListado.js` para decidir "vacío vs. con resultados": esa
   decisión queda como un condicional simple dentro de
   `ClienteListado.jsx` (`customers.length === 0`).
   **Justificación:** a diferencia de `bajaCliente.js` o
   `clienteEdicion.js` (que interpretan 2-3 estados de negocio reales
   devueltos por el backend), acá la única regla real —qué cuenta como
   coincidencia— ya vive en `core.py`/`repository.py`; envolver un
   `if` trivial en un módulo aparte sería una abstracción sin
   contenido, contraria a la simplicidad pedida por el proyecto.
   **Alternativa descartada:** un módulo puro `clienteListado.js` con una
   función `evaluateListado(customers)` — descartada por no encapsular
   ninguna regla de negocio real. *(RF-5)*

6. **Decisión Tomada:** paginación con `page` + `has_next` (sin `total` ni
   `total_pages` en la respuesta del backend); `has_previous` se calcula en
   el Frontend como `page > 1`.
   **Justificación:** RF-8 solo pide navegación Anterior/Siguiente, no
   números de página ni conteo total visible; devolver menos campos que los
   necesarios evita mantener un contrato más grande del que la UI consume.
   **Alternativa descartada:** devolver `total`/`total_pages` para una
   futura UI con números de página — descartada por anticipar un requisito
   que no está pedido (fuera de alcance: "ordenamiento/paginación
   configurable"). *(RF-8)*

## 5. Estrategia de Tests

### Tests unitarios (`core.py`, sin base de datos)
- `normalize_search_text`: `"Pérez"` y `"perez"` normalizan al mismo valor;
  `"ÑOÑO"` y `"ñoño"` también. [Cubre RF-4]
- `matches_search`: coincidencia parcial por nombre, por apellido y por
  DNI (ej. `"301112"` coincide con el cliente de DNI `30111222`); un
  criterio que no aparece en ningún campo no coincide. [Cubre RF-2, RF-3]

### Tests de integración (`repository.py`, SQLite temporal)
- `list_customers` sin `query` devuelve todos los clientes, Activos e
  Inactivos. [Cubre RF-1, RF-6]
- `list_customers` con un `query` que coincide por nombre/apellido/DNI
  devuelve solo esos clientes. [Cubre RF-2, RF-3]
- `list_customers` con un `query` sin coincidencias devuelve una lista
  vacía. [Cubre RF-5]
- `list_customers` con más de 20 clientes devuelve solo los primeros 20 y
  `has_next=True`; la página 2 devuelve el resto con `has_next=False`.
  [Cubre RF-8]

### Tests de integración (`routes/clientes.py`, `TestClient`)
- `GET /clientes` sin `q` devuelve todos los clientes creados en el test,
  incluido uno dado de baja. [Cubre RF-1, RF-6]
- `GET /clientes?q=...` con coincidencia parcial e insensible a
  mayúsculas/tildes devuelve solo los clientes esperados. [Cubre RF-2,
  RF-3, RF-4]
- `GET /clientes?q=...` sin coincidencias devuelve `"customers": []`.
  [Cubre RF-5]
- `GET /clientes?page=2` sobre un conjunto de más de 20 clientes devuelve
  el resto y `has_next=False`. [Cubre RF-8]

### Tests E2E (Vitest + React Testing Library sobre `ClienteListado.jsx`)
Con `listarClientes` mockeado (sin red real):
- Al montar el componente, se pide la página 1 sin filtro y se renderiza la
  tabla con los clientes devueltos. [Cubre RF-1]
- Buscar un criterio sin resultados muestra "no se encontraron
  resultados" en vez de una tabla vacía. [Cubre RF-5]
- Borrar el criterio de búsqueda vuelve a pedir la lista completa (página
  1, sin `q`). [Cubre RF-7]
- Con `has_next: true`, el botón "Siguiente" está habilitado y, al
  hacer clic, pide la página 2; con `has_next: false`, el botón está
  deshabilitado. [Cubre RF-8]
- Cambiar el criterio de búsqueda estando en la página 2 vuelve a pedir la
  página 1 con el nuevo criterio. [Cubre RF-8]

## Cumplimiento de la constitución
- **Regla 1 (stack fijo):** se reutiliza FastAPI + SQLAlchemy y React, sin
  agregar dependencias (se descartaron explícitamente una extensión SQLite
  y un mecanismo de debounce; ver Decisiones 1 y 4).
- **Regla 2 (spec antes que código):** este plan parte de
  `specs/004-listar-clientes/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz):** `core.py` concentra la
  regla real de "qué es una coincidencia", testeable sin HTTP ni React.
- **Regla 4 (tests obligatorios):** la estrategia cubre los ocho RF de la
  spec antes de considerar la feature terminada.
- **Regla 5 (persistencia única):** `list_customers` lee exclusivamente de
  `database.py`/la tabla `customers`; no hay estado ad-hoc nuevo.
- **Regla 6 (idioma consistente):** identificadores en inglés
  (`list_customers`, `matches_search`, `ClienteListado.jsx`); mensajes al
  Administrador en español ("No se encontraron resultados").
