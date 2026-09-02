# Tasks 019 — Correcciones sobre Cliente, Producto y Venta

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta. Las cuatro correcciones
(H1-H4) son independientes entre sí, así que se agrupan en fases por
corrección, no por capa.

## Fase 0 — H1 (Cliente Inactivo): backend

- [x] **T01 — Constante de mensaje y bloqueo en `editar_cliente`**
  En `app/backend/routes/clientes.py`: agregar
  `CUSTOMER_INACTIVE_MESSAGE = "El cliente está inactivo y no puede
  modificarse"`. En `editar_cliente`, justo después de encontrar al
  cliente por `dni` y antes de normalizar/validar el payload, si
  `customer.status == ClientStatus.INACTIVE` devolver `422` con
  `{"errors": [{"field": "status", "message":
  CUSTOMER_INACTIVE_MESSAGE}]}` sin tocar `repository.update_customer`.
  [Cubre RF-2]
  Hecho cuando: `pytest -q -k editar_cliente_inactivo_bloquea` pasa,
  devolviendo `422` con ese mensaje y confirmando (con un `GET
  /clientes/{dni}` posterior) que ninguno de sus datos cambió.

- [x] **T02 — Actualizar el test existente de edición sobre Inactivo**
  El test actual `test_editar_cliente_inactivo_guarda_los_cambios_sin_reactivarlo`
  en `tests/backend/test_routes_clientes.py` asumía que la edición de un
  Inactivo se permitía; reemplazarlo por el nuevo comportamiento (o
  fusionarlo con T01) para que no quede un test verde que contradiga la
  regla nueva.
  [Cubre RF-2, no regresión]
  Hecho cuando: `pytest -q tests/backend/test_routes_clientes.py` pasa
  completo, sin ningún test que siga afirmando que editar un Inactivo
  persiste cambios.

- [x] **T03 — Confirmar que editar un cliente Activo sigue sin cambios**
  Verificar (agregando el caso si no está ya cubierto) que
  `test_editar_cliente_activo_guarda_los_cambios` y los demás tests de
  edición sobre Activos siguen pasando tal cual, sin ningún `422` nuevo
  de por medio.
  [Cubre RF-3]
  Hecho cuando: `pytest -q -k "editar_cliente_activo"` pasa sin cambios
  de comportamiento.

## Fase 1 — H1 (Cliente Inactivo): frontend

- [x] **T04 — Estado `INACTIVE` en `evaluateEdicionBusqueda`**
  En `app/frontend/clienteEdicion.js`: agregar
  `INACTIVE_MESSAGE = "El cliente está inactivo y no puede modificarse"`
  y un tercer estado `EDICION_STATE.INACTIVE`. Si
  `searchResult.success && searchResult.customer.status === "Inactivo"`,
  devolver `{ state: "INACTIVE", message: INACTIVE_MESSAGE, customer }`
  en vez de `FOUND`.
  [Cubre RF-1]
  Hecho cuando: `npm run test -- clienteEdicion` pasa, con un caso para
  cliente Activo (`FOUND`), uno Inactivo (`INACTIVE` + mensaje) y uno
  sin resultados (`NOT_FOUND`, sin cambios).

- [x] **T05 — `ClienteEdicionForm.jsx` no muestra el formulario si el estado es `INACTIVE`**
  Cuando `evaluateEdicionBusqueda` devuelve `INACTIVE`, mostrar el
  mensaje (mismo patrón visual que el banner de `NOT_FOUND`) y no
  llamar a `setFormValues`/`setEditingDni`, por lo que el formulario y
  el botón "Guardar cambios" no se renderizan.
  [Cubre RF-1]
  Hecho cuando: `npm run test -- ClienteEdicionForm` pasa, cubriendo:
  buscar un DNI de cliente Inactivo muestra el mensaje y no aparece
  ningún campo de formulario ni el botón "Guardar cambios".

## Fase 2 — H2 (Leyenda SKU)

- [x] **T06 — Cambiar el `hint` del campo `sku`**
  En `app/frontend/productoFields.js`, cambiar el `hint` de la entrada
  `sku` de `"Cualquier texto, sin espacios al inicio/fin"` a
  `"Identificador único del producto"`. No tocar ningún otro campo ni
  la validación de `sku`.
  [Cubre RF-4, RF-5]
  Hecho cuando: `npm run test -- ProductoForm` pasa, con un caso que
  verifica que el texto de ayuda visible bajo Código/SKU es
  "Identificador único del producto".

## Fase 3 — H3 (Modal de detalle de venta)

- [x] **T07 — Estilos reales de modal en `VentasListado.css`**
  Agregar `.ventas-listado__modal-backdrop` (`position: fixed`, cubre
  todo el viewport, fondo semitransparente oscuro, `z-index` alto,
  centra su contenido) y `.ventas-listado__modal` (tarjeta con fondo
  sólido, borde redondeado, ancho máximo, `max-height` con scroll
  interno). No tocar el JSX en esta tarea.
  [Cubre RF-6, RF-9]
  Hecho cuando: revisión visual manual (`npm run dev`, abrir el
  listado de ventas, click en ver detalle) confirma que el modal se ve
  superpuesto con fondo oscurecido y centrado, no como contenido
  inline de la página.

- [x] **T08 — Ícono SVG de ver detalle (reemplaza el emoji)**
  En `VentasListado.jsx`, reemplazar el contenido `👁` del botón por un
  `<svg>` inline de "ojo", manteniendo el `aria-label` existente
  (`Ver detalle de la venta ${sale.id}`).
  [Cubre RF-7]
  Hecho cuando: `npm run test -- VentasListado` pasa, con un caso que
  verifica que el botón de ver detalle contiene un `<svg>` y no el
  texto/emoji `👁`.

- [x] **T09 — Botón de cierre con ícono "X"**
  En el modal de `VentasListado.jsx`, agregar un botón con un `<svg>`
  de "X" y `aria-label="Cerrar detalle"` que llama a
  `handleCloseDetail` (ya existente), además del botón "Cerrar" de
  texto actual.
  [Cubre RF-8]
  Hecho cuando: `npm run test -- VentasListado` pasa, con un caso que
  hace click en el botón con `aria-label="Cerrar detalle"` y verifica
  que el modal deja de estar en el DOM.

## Fase 4 — H4 (Filtro de clientes por campo): backend

- [x] **T10 — `core.matches_search_field`**
  En `app/backend/core.py`, agregar
  `matches_search_field(normalized_query, field, *, dni, first_name,
  last_name)`: para `"first_name"`/`"last_name"` aplica
  `normalize_search_text` + coincidencia parcial sobre ese campo
  únicamente; para `"dni"` compara contra `str(dni)`. No modificar
  `matches_search` todavía.
  [Cubre RF-11, RF-12]
  Hecho cuando: `pytest -q -k matches_search_field` pasa en
  `tests/backend/test_core.py`, cubriendo los tres campos por separado
  y confirmando que un valor que matchea `first_name` no matchea
  cuando `field="last_name"`.

- [x] **T11 — `repository.list_customers` recibe y usa `field`**
  En `app/backend/repository.py`, agregar el parámetro `field` a
  `list_customers` y usar `core.matches_search_field` en vez de
  `core.matches_search` cuando hay `query`. Sin `query`, el
  comportamiento no cambia (se ignora `field`). Eliminar
  `core.matches_search` si queda sin otros usos.
  [Cubre RF-11, RF-14, RF-15]
  Hecho cuando: `pytest -q -k list_customers` pasa, incluyendo un caso
  con `field="last_name"` que no devuelve clientes que solo coinciden
  por `first_name`.

- [x] **T12 — `GET /clientes` acepta `field`**
  En `app/backend/routes/clientes.py`, agregar el query param `field`
  (`str | None`, default `"first_name"` si se omite o llega vacío) a
  `listar_clientes` y pasarlo a `repository.list_customers`.
  [Cubre RF-10, RF-11]
  Hecho cuando: `pytest -q -k listar_clientes_con_field` pasa en
  `tests/backend/test_routes_clientes.py`, con casos para
  `field=first_name`, `field=last_name` y `field=dni` que devuelven
  solo coincidencias contra ese campo, y un caso sin `field` ni `q` que
  sigue devolviendo el listado completo paginado.

## Fase 5 — H4 (Filtro de clientes por campo): frontend

- [x] **T13 — `listarClientes` envía `field`**
  En `app/frontend/api/clientesApi.js`, agregar `field` a las opciones
  de `listarClientes({ q, field, page })`, incluyéndolo como query
  param cuando está presente.
  [Cubre RF-10, RF-11, wiring]
  Hecho cuando: `npm run test -- clientesApi` pasa, verificando que la
  URL construida incluye `field=...` cuando se pasa esa opción.

- [x] **T14 — `<select>` de campo + input de valor en `ClienteListado.jsx`**
  Reemplazar el `<input>` único por un `<select>` (`Nombre` /
  `Apellido` / `DNI`, valores `first_name`/`last_name`/`dni`, default
  `first_name`) más el `<input>` de valor ya existente. Dos estados:
  `fieldInput` (cambia libremente) y `appliedField` (se fija recién en
  `handleSearch`, igual patrón que `appliedQuery`). Pasar
  `field: appliedField` a `listarClientes`.
  [Cubre RF-10, RF-11, RF-13]
  Hecho cuando: `npm run test -- ClienteListado` pasa, cubriendo:
  "Nombre" seleccionado por defecto; cambiar el `<select>` sin
  presionar "Buscar" no dispara una nueva llamada a `listarClientes`;
  presionar "Buscar" con "DNI" elegido llama a `listarClientes` con
  `field: "dni"` y el valor ingresado; presionar "Buscar" con el valor
  vacío llama sin `q` (muestra el listado completo, RF-14).

## Fase 6 — Cierre

- [x] **T15 — Suite completa en verde**
  Correr toda la suite de backend y frontend para confirmar que no
  quedó ninguna regresión entre las cuatro correcciones.
  [Soporte - sin RF directo]
  Hecho cuando: `pytest -q` y `npm run test` pasan completos, y
  `npm run typecheck` no reporta errores nuevos.
