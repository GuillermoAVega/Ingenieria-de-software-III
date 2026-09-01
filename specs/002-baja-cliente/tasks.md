# Tasks 002 — Baja de Cliente

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Andamiaje

- [x] **T01 — Crear archivos vacíos**
  Crear `app/frontend/bajaCliente.js` y
  `app/frontend/components/ClienteBajaForm.jsx`, según la estructura de
  `plan.md`. No se crean archivos nuevos en el backend (se extienden los
  existentes de [[001-alta-cliente]]).
  RF: — (base para todas las tareas siguientes)
  Hecho cuando: los archivos existen y `npm run test` sigue corriendo sin
  errores de recolección.

## Fase 1 — Backend: núcleo y repositorio

- [x] **T02 — `try_normalize_dni` en `core.py`**
  Implementar la función que intenta convertir un DNI a entero y devuelve
  `None` si no es numérico, con sus tests unitarios.
  RF: RF-2
  Hecho cuando: `pytest -q -k try_normalize_dni` pasa, cubriendo
  `"0123456"`/`"123456"` (mismo valor), `"abc"` y `"30.111.222"` (ambos
  `None`).

- [x] **T03 — `find_by_dni` en `repository.py`**
  Implementar la búsqueda de solo lectura por DNI (usando
  `try_normalize_dni`), con tests de integración sobre SQLite temporal.
  RF: RF-1, RF-2
  Hecho cuando: `pytest -q -k find_by_dni` pasa, cubriendo DNI exacto, DNI
  con cero a la izquierda, DNI de formato inválido (devuelve `None`, no
  lanza excepción) y DNI inexistente (devuelve `None`).

- [x] **T04 — `deactivate_by_dni` en `repository.py`**
  Implementar el cambio de estado a Inactivo sin re-verificar el estado
  previo, con tests de integración.
  RF: RF-4, RF-7, RF-8
  Hecho cuando: `pytest -q -k deactivate_by_dni` pasa, cubriendo cliente
  Activo → Inactivo persistido, DNI inexistente (devuelve `None`) y cliente
  ya Inactivo (no lanza error, permanece Inactivo).

## Fase 2 — Backend: rutas

- [x] **T05 — Endpoint `GET /clientes/{dni}` (búsqueda)**
  Implementar la ruta de búsqueda usando `find_by_dni`, con tests de
  integración vía `TestClient`.
  RF: RF-1, RF-2
  Hecho cuando: `pytest -q -k buscar_cliente_endpoint` pasa, cubriendo
  cliente Activo (200), cliente Inactivo (200, informa el estado), DNI
  inexistente (404) y DNI de formato inválido (404, mismo mensaje).

- [x] **T06 — Endpoint `PATCH /clientes/{dni}/baja`**
  Implementar la ruta de baja usando `deactivate_by_dni`, con tests de
  integración vía `TestClient`.
  RF: RF-4, RF-7, RF-8
  Hecho cuando: `pytest -q -k baja_cliente_endpoint` pasa, cubriendo baja
  exitosa sobre cliente Activo (200 + estado persistido en Inactivo), DNI
  inexistente (404), e invocación directa sobre cliente ya Inactivo (200,
  documentando el comportamiento aceptado de RF-8).

## Fase 3 — Frontend: lógica pura y API

- [x] **T07 — `bajaCliente.js`**
  Implementar la función pura que interpreta el resultado de la búsqueda
  (no encontrado / ya inactivo / requiere confirmación) y sus mensajes en
  español, con tests unitarios sin React.
  RF: RF-2, RF-3, RF-6
  Hecho cuando: `npm run test -- bajaCliente` pasa, cubriendo los tres
  estados posibles.

- [x] **T08 — `buscarCliente` y `darDeBajaCliente` en `clientesApi.js`**
  Implementar ambas funciones de comunicación con los endpoints nuevos, con
  tests con `fetch` mockeado.
  RF: RF-1, RF-2, RF-4
  Hecho cuando: `npm run test -- clientesApi` pasa, cubriendo respuestas de
  éxito y de error (404) para ambas funciones.

## Fase 4 — Frontend: componente

- [x] **T09 — Esqueleto de `ClienteBajaForm.jsx`: búsqueda y "no encontrado"**
  Implementar el input de DNI, el botón de búsqueda, la llamada a
  `buscarCliente` y el mensaje de "no encontrado" usando `bajaCliente.js`.
  RF: RF-1, RF-2
  Hecho cuando: un test de RTL, con `buscarCliente` mockeado devolviendo "no
  encontrado", muestra el mensaje correspondiente y no renderiza ningún
  botón de confirmación.

- [x] **T10 — Render de "cliente ya inactivo"**
  Extender `ClienteBajaForm.jsx` para mostrar el mensaje de `bajaCliente.js`
  cuando el cliente encontrado ya está Inactivo, sin botón de confirmación.
  RF: RF-6
  Hecho cuando: un test de RTL, con `buscarCliente` mockeado devolviendo un
  cliente Inactivo, muestra el mensaje de "ya dado de baja" y
  `darDeBajaCliente` no se invoca.

- [x] **T11 — Diálogo de confirmación para cliente Activo**
  Extender `ClienteBajaForm.jsx` para mostrar los datos del cliente y los
  botones "Confirmar"/"Cancelar" cuando el cliente encontrado está Activo.
  RF: RF-3
  Hecho cuando: un test de RTL, con `buscarCliente` mockeado devolviendo un
  cliente Activo, muestra sus datos junto a ambos botones.

- [x] **T12 — Confirmar baja**
  Conectar el botón "Confirmar" a `darDeBajaCliente` y mostrar "Cliente dado
  de baja exitosamente" al recibir éxito.
  RF: RF-4
  Hecho cuando: un test de RTL, con `darDeBajaCliente` mockeado devolviendo
  éxito, confirma que se invoca la función y se muestra el mensaje.

- [x] **T13 — Cancelar confirmación**
  Conectar el botón "Cancelar" para cerrar el diálogo de confirmación sin
  invocar ninguna API.
  RF: RF-5
  Hecho cuando: un test de RTL confirma que, tras el click en "Cancelar",
  `darDeBajaCliente` NO fue invocada.

## Fase 5 — Integración de navegación

- [x] **T14 — Selector de pestañas en `App.jsx`**
  Agregar la vista "Baja de Cliente" (`ClienteBajaForm`) junto a la de
  "Alta de Cliente" existente, con un selector simple basado en `useState`.
  RF: — (estructural)
  Hecho cuando: `npm run typecheck` pasa y una revisión manual en el
  navegador permite alternar entre ambas vistas sin recargar la página.

## Fase 6 — Verificación final

- [x] **T15 — Verificación completa contra la matriz de trazabilidad**
  Revisar la matriz de trazabilidad de `plan.md` y confirmar que cada RF-1 a
  RF-8 tiene al menos un test en verde asociado.
  RF: RF-1 a RF-8 (verificación de cobertura total)
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada fila de la matriz de trazabilidad
  tiene un test correspondiente pasando.
