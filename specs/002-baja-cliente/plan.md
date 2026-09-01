# Plan 002 — Baja de Cliente

Plan técnico para implementar `specs/002-baja-cliente/spec.md`, respetando
`docs/constitution.md` y reutilizando lo ya construido en
[[001-alta-cliente]] (`Customer`, `ClientStatus`, capas `core.py` /
`repository.py` / `routes/clientes.py` / `clientesApi.js`). Este documento no
contiene código: describe estructura, decisiones y estrategia de
verificación.

## Estructura de módulos

### Backend (`app/backend/`)

| Módulo | Responsabilidad | RF que cubre |
|---|---|---|
| `core.py` (extendido) | Agrega `try_normalize_dni`, que intenta convertir un DNI a su valor numérico y devuelve `None` si el valor no es convertible (letras, puntos, vacío), en vez de lanzar una excepción. No reemplaza a `normalize_dni`, que sigue usando el alta sobre datos ya validados. | RF-2 |
| `repository.py` (extendido) | Agrega `find_by_dni` (búsqueda de solo lectura por DNI normalizado, sin exigir formato válido) y `deactivate_by_dni` (cambia el estado del cliente encontrado a Inactivo y persiste, sin comprobar cuál era su estado previo). Ninguna de las dos elimina filas. | RF-1, RF-2, RF-4, RF-7, RF-8 |
| `routes/clientes.py` (extendido) | Agrega `GET /clientes/{dni}` (búsqueda: 200 con los datos y el estado del cliente si existe, 404 con advertencia si no) y `PATCH /clientes/{dni}/baja` (ejecuta la baja: 404 si el DNI no existe, 200 con mensaje de éxito y los datos actualizados si existe). | RF-1, RF-2, RF-4, RF-7, RF-8 |

### Frontend (`app/frontend/`)

| Módulo | Responsabilidad | RF que cubre |
|---|---|---|
| `bajaCliente.js` (nuevo) | Módulo puro, sin dependencia de React. A partir del resultado de la búsqueda, decide entre tres estados ("no encontrado", "ya inactivo", "requiere confirmación") y expone los textos de advertencia/éxito en español para cada uno. Testeable sin renderizar UI. | RF-2, RF-3, RF-6 |
| `components/ClienteBajaForm.jsx` (nuevo) | Formulario de búsqueda por DNI. Llama a `buscarCliente`, delega en `bajaCliente.js` qué estado mostrar, y solo si corresponde muestra el diálogo de confirmación. Al confirmar, llama a `darDeBajaCliente` y muestra el resultado; al cancelar, no llama a ninguna API. | RF-1 a RF-6 |
| `api/clientesApi.js` (extendido) | Agrega `buscarCliente(dni)` (`GET /clientes/{dni}`) y `darDeBajaCliente(dni)` (`PATCH /clientes/{dni}/baja`), con la misma forma de traducción éxito/error que la función `altaCliente` ya existente. | RF-1, RF-2, RF-4 |
| `App.jsx` (extendido) | Agrega un selector simple entre la vista "Alta de Cliente" (existente) y la nueva "Baja de Cliente". | Estructural, sin RF directo |

## Decisiones técnicas

1. **Reutilizar `models.py` (`Customer`, `ClientStatus`) sin agregar tablas
   nuevas.** La baja es únicamente un cambio del campo `status` sobre el
   mismo modelo de [[001-alta-cliente]].
   Justificación: RF-7 exige no eliminar el registro, solo cambiar su
   estado; el modelo ya soporta `Activo`/`Inactivo`.
   Alternativa descartada: una tabla `bajas` separada, referenciando al
   cliente — descartada porque no hay requisito de auditoría de bajas
   (explícitamente fuera de alcance de la spec). *(RF-4, RF-7)*

2. **Separar `find_by_dni` (lectura) de `deactivate_by_dni` (escritura) en
   `repository.py`**, en vez de una única función que busque y decida
   internamente si dar de baja.
   Justificación: RF-1 (búsqueda) y RF-4 (ejecución de la baja) son dos
   interacciones separadas en el tiempo, con una confirmación explícita del
   Administrador entre medio (RF-3); separarlas en el repositorio refleja
   ese límite y permite que la búsqueda sea una operación de solo lectura,
   sin efectos secundarios.
   Alternativa descartada: una función combinada `buscar_y_dar_de_baja` —
   descartada porque no permitiría exponer un endpoint de solo lectura para
   la búsqueda. *(RF-1, RF-4)*

3. **`try_normalize_dni` en `core.py` devuelve `None` ante un valor no
   numérico**, en vez de reutilizar `normalize_dni` (que asume formato ya
   validado y lanza `ValueError`).
   Justificación: RF-2 decide explícitamente no validar el formato del DNI
   en la búsqueda; un DNI con letras, puntos o guiones debe tratarse como
   "no encontrado", nunca como un error del servidor.
   Alternativa descartada: envolver `normalize_dni` en `try/except`
   directamente dentro de `repository.py` — descartada porque duplicaría el
   manejo de la excepción en cada lugar que necesite buscar por DNI, en vez
   de centralizarlo en una función pura y testeable. *(RF-2)*

4. **Endpoint de baja sin body y sin aceptar un valor de estado como
   parámetro** (`PATCH /clientes/{dni}/baja`), en vez de un endpoint
   genérico `PATCH /clientes/{dni}` que reciba `{"status": ...}`.
   Justificación: la reactivación de un cliente Inactivo está explícitamente
   fuera de alcance de esta spec; un endpoint genérico de cambio de estado
   habilitaría reactivar clientes sin que exista ese requisito ni sus
   validaciones.
   Alternativa descartada: endpoint genérico de actualización de estado —
   descartada por exceder el alcance definido en la spec. *(Fuera de
   alcance, RF-4)*

5. **El endpoint de baja no vuelve a consultar si el cliente sigue Activo
   antes de aplicar el cambio**; fija el estado en Inactivo directamente.
   Justificación: decisión explícita de RF-8, resuelta en la entrevista de
   la spec, que asume un único Administrador operando el sistema.
   Riesgo aceptado: si `PATCH /clientes/{dni}/baja` se invoca directamente
   sobre un cliente ya Inactivo (sin pasar por la búsqueda del Frontend), el
   sistema responde con el mensaje de éxito genérico en lugar de la
   advertencia de RF-6 — esa advertencia es responsabilidad exclusiva del
   paso de búsqueda/localización (RF-1, RF-2, RF-6), no del paso de
   confirmación. Este comportamiento queda cubierto por un test dedicado
   (ver Estrategia de tests) para que sea explícito y no un olvido.
   Alternativa descartada: re-consultar el estado dentro del endpoint de
   baja y devolver la advertencia de RF-6 si ya es Inactivo — descartada
   porque RF-8 decide explícitamente lo contrario. *(RF-8)*

6. **La interpretación del resultado de la búsqueda (no encontrado / ya
   inactivo / requiere confirmación) vive en el módulo puro
   `bajaCliente.js`**, no directamente en el JSX de `ClienteBajaForm.jsx`.
   Justificación: regla 3 de la constitución — la lógica de negocio debe ser
   testeable sin renderizar UI, igual que `validation.js` en
   [[001-alta-cliente]].
   Alternativa descartada: un `if/else` inline dentro del componente —
   descartada porque acoplaría la regla de negocio al componente React.
   *(RF-2, RF-3, RF-6)*

7. **Navegación entre "Alta de Cliente" y "Baja de Cliente" con un selector
   de pestañas usando `useState` en `App.jsx`**, sin agregar una librería de
   ruteo.
   Justificación: solo hay dos vistas y ninguna necesidad de URLs
   distintas; la constitución regla 1 exige justificar cualquier framework
   adicional.
   Alternativa descartada: incorporar `react-router-dom` — descartada por no
   estar justificada para dos vistas sin necesidad de rutas. *(Estructural)*

## Estrategia de tests

### Backend — tests unitarios sobre `core.py` (sin base de datos, sin HTTP)
- `try_normalize_dni`: `"0123456"` y `"123456"` devuelven el mismo entero;
  `"abc"` y `"30.111.222"` devuelven `None`. *(RF-2)*

### Backend — tests de integración sobre `repository.py` (SQLite temporal)
- `find_by_dni` encuentra al cliente tanto por el DNI exacto como por su
  variante con ceros a la izquierda. *(RF-1)*
- `find_by_dni` devuelve `None` ante un DNI de formato inválido (no
  numérico), sin lanzar excepción. *(RF-2)*
- `find_by_dni` devuelve `None` si no existe ningún cliente con ese DNI.
  *(RF-2)*
- `deactivate_by_dni` cambia el estado de Activo a Inactivo y lo persiste.
  *(RF-4, RF-7)*
- `deactivate_by_dni` devuelve `None` si el DNI no existe. *(RF-4)*
- `deactivate_by_dni` invocado sobre un cliente ya Inactivo no lanza error y
  deja el estado en Inactivo (comportamiento idempotente aceptado por
  RF-8). *(RF-8)*

### Backend — tests de integración sobre `routes/clientes.py` (`TestClient`)
- `GET /clientes/{dni}` sobre un cliente Activo devuelve 200 con
  `status: "Activo"`. *(RF-1)*
- `GET /clientes/{dni}` sobre un cliente Inactivo devuelve 200 con
  `status: "Inactivo"` (la ruta informa, no filtra). *(RF-1)*
- `GET /clientes/{dni}` con un DNI inexistente devuelve 404 con la
  advertencia de "no encontrado". *(RF-2)*
- `GET /clientes/{dni}` con un DNI de formato inválido devuelve 404 (mismo
  mensaje que "no encontrado", nunca 500). *(RF-2)*
- `PATCH /clientes/{dni}/baja` sobre un cliente Activo devuelve 200 con el
  mensaje de éxito, y una búsqueda posterior confirma `status: "Inactivo"`.
  *(RF-4, RF-7)*
- `PATCH /clientes/{dni}/baja` con un DNI inexistente devuelve 404. *(RF-4)*
- `PATCH /clientes/{dni}/baja` invocado directamente sobre un cliente ya
  Inactivo devuelve 200 igual (documenta el riesgo aceptado de la decisión
  técnica 5). *(RF-8)*

### Frontend — tests unitarios sobre `bajaCliente.js` (sin React)
- Resultado "no encontrado" → estado `NO_ENCONTRADO`, sin requerir
  confirmación. *(RF-2)*
- Cliente Activo → estado `REQUIERE_CONFIRMACION`. *(RF-3)*
- Cliente Inactivo → estado `YA_INACTIVO`, sin requerir confirmación.
  *(RF-6)*

### Frontend — tests sobre `clientesApi.js` (fetch mockeado)
- `buscarCliente`: traduce una respuesta 200 y una 404 a la forma esperada.
  *(RF-1, RF-2)*
- `darDeBajaCliente`: traduce una respuesta 200 y una 404 a la forma
  esperada. *(RF-4)*

### Frontend — Vitest + React Testing Library sobre `ClienteBajaForm.jsx`
Con `clientesApi.js` mockeado (sin red real):
- Buscar un DNI inexistente: se muestra "cliente no encontrado" y no se
  renderiza ningún botón de confirmación. *(RF-2)*
- Buscar un DNI de un cliente Inactivo: se muestra "ya se encuentra dado de
  baja"; no se renderiza botón de confirmación ni se invoca
  `darDeBajaCliente`. *(RF-6)*
- Buscar un DNI de un cliente Activo: se muestran sus datos junto a los
  botones "Confirmar" y "Cancelar". *(RF-3)*
- Click en "Confirmar": se invoca `darDeBajaCliente` y se muestra "Cliente
  dado de baja exitosamente". *(RF-4)*
- Click en "Cancelar": NO se invoca `darDeBajaCliente`; el cliente
  permanece sin cambios. *(RF-5)*

### Verificación de tipado
`npm run typecheck` (JSDoc + `tsc --checkJs`) se ejecuta como parte del
pipeline de verificación de cada tarea, igual que en 001; no reemplaza a los
tests funcionales de Vitest.

## Matriz de trazabilidad

| Requisito | Módulo(s) que lo implementa | Test(s) que lo cubre |
|---|---|---|
| RF-1 | `repository.py` (`find_by_dni`), `routes/clientes.py` (`GET`), `clientesApi.js` (`buscarCliente`), `ClienteBajaForm.jsx` | test de integración de búsqueda (activo/inactivo/ceros a la izquierda) |
| RF-2 | `core.py` (`try_normalize_dni`), `repository.py`, `routes/clientes.py`, `bajaCliente.js` | test unitario de `try_normalize_dni`; test de integración de "no encontrado" y formato inválido; test de `bajaCliente.js` |
| RF-3 | `bajaCliente.js`, `ClienteBajaForm.jsx` | test unitario de `bajaCliente.js`; test de RTL de diálogo de confirmación |
| RF-4 | `repository.py` (`deactivate_by_dni`), `routes/clientes.py` (`PATCH`), `clientesApi.js` (`darDeBajaCliente`), `ClienteBajaForm.jsx` | test de integración de baja exitosa; test de RTL de confirmación |
| RF-5 | `ClienteBajaForm.jsx` | test de RTL de cancelación (sin llamada a la API) |
| RF-6 | `bajaCliente.js`, `ClienteBajaForm.jsx` | test unitario de `bajaCliente.js`; test de RTL de cliente ya inactivo |
| RF-7 | `repository.py`, `models.py` (reutilizado) | test de integración que confirma que el registro persiste tras la baja, solo con el estado modificado |
| RF-8 | `repository.py` (`deactivate_by_dni`), `routes/clientes.py` (`PATCH`) | test de integración de baja idempotente sobre cliente ya inactivo |
| NFR — idioma español de mensajes | `routes/clientes.py`, `bajaCliente.js` | verificado por assertions de texto exacto en los tests de RF-2, RF-3, RF-6 |
| NFR — persistencia única | `database.py` (reutilizado), `repository.py` | cubierto por diseño (ya validado en 001), sin test dedicado nuevo |

## Cumplimiento de la constitución

- **Regla 1 (stack fijo)**: se reutiliza FastAPI + Pydantic + SQLAlchemy en
  el backend y React + JavaScript + JSDoc en el frontend, sin introducir
  ningún framework adicional (ver decisión técnica 7).
- **Regla 2 (spec antes que código)**: este plan se redacta a partir de
  `specs/002-baja-cliente/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz)**: `bajaCliente.js` concentra
  la interpretación del resultado de la búsqueda y es testeable sin
  renderizar ningún componente React (decisión técnica 6); `ClienteBajaForm.jsx`
  solo orquesta llamadas y renderizado.
- **Regla 4 (tests obligatorios)**: la estrategia de tests cubre los ocho RF
  de la spec, incluido el comportamiento aceptado de RF-8, antes de
  considerar la feature terminada.
- **Regla 5 (persistencia única)**: la baja se aplica exclusivamente sobre
  `Customer` vía `repository.py`/`database.py`; no hay estado ad-hoc nuevo.
- **Regla 6 (idioma consistente)**: identificadores de código en inglés
  (`find_by_dni`, `deactivate_by_dni`, `ClienteBajaForm.jsx`, etc.); mensajes
  al Administrador en español, definidos como texto explícito en
  `bajaCliente.js` y `routes/clientes.py`.
