# Tasks 001 — Alta de Cliente

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Andamiaje

- [x] **T01 — Crear estructura de archivos vacíos**
  Crear `app/backend/core.py`, `models.py`, `schemas.py`, `repository.py`,
  `database.py`, `routes/clientes.py`, `scripts/seed_clientes_ficticios.py`,
  y `app/frontend/components/ClienteForm.jsx`,
  `app/frontend/api/clientesApi.js`, según la estructura de `plan.md`.
  RF: — (base para todas las tareas siguientes)
  Hecho cuando: todos los archivos existen y `pytest -q` corre sin errores
  de recolección (aunque no haya tests todavía).

## Fase 1 — Núcleo de validación (`core.py`)

- [x] **T02 — Validación de nombre y apellido**
  Implementar en `core.py` la función que valida nombre/apellido y sus
  tests unitarios.
  RF: RF-2
  Hecho cuando: `pytest -q -k nombre_apellido` pasa, cubriendo al menos:
  "María José" (válido), "Juan123" (inválido), "O'Connor" (inválido),
  "Müller" (inválido, alfabeto no español), "   " (no aplica aquí, ver T06).

- [x] **T03 — Validación de email**
  Implementar en `core.py` la función que valida el email según
  `usuario@dominio` sin punto en el dominio, y sus tests unitarios.
  RF: RF-3
  Hecho cuando: `pytest -q -k email` pasa, cubriendo "user@dominio" (válido)
  y "user@dominio.com" (inválido), "userdominio" (inválido, sin @).
  **Regla revertida en T25** (Fase 7): ahora un email con TLD es el válido.

- [x] **T04 — Validación de teléfono**
  Implementar en `core.py` la función que valida que el teléfono solo tenga
  dígitos y guiones, y sus tests unitarios.
  RF: RF-4
  Hecho cuando: `pytest -q -k telefono` pasa, cubriendo "11-4444-5555"
  (válido) y "11-abcd" (inválido).

- [x] **T05 — Validación de formato de DNI**
  Implementar en `core.py` la función que valida que el DNI sea numérico de
  7 u 8 dígitos, y sus tests unitarios.
  RF: RF-5
  Hecho cuando: `pytest -q -k dni_formato` pasa, cubriendo "30111222"
  (válido), "301112" (inválido, 6 dígitos), "30.111.222" (inválido).

- [x] **T06 — Normalización de espacios (trim)**
  Implementar en `core.py` la función que recorta el espacio simple al
  inicio/fin de un campo de texto, y sus tests unitarios.
  RF: RF-10
  Hecho cuando: `pytest -q -k trim` pasa, cubriendo `" Juan "` → `"Juan"` y
  confirmando que un tab (`"\tJuan"`) NO se recorta.

- [x] **T07 — Normalización numérica del DNI**
  Implementar en `core.py` la función auxiliar que normaliza un DNI a su
  valor numérico (para comparación de duplicados), y sus tests unitarios.
  RF: RF-6 (parte de normalización)
  Hecho cuando: `pytest -q -k dni_normaliza` pasa, verificando que
  `"0123456"` y `"123456"` normalizan al mismo valor.

- [x] **T08 — Asignación del estado inicial**
  Implementar en `core.py` la función que asigna estado "Activo" a todo
  cliente nuevo, sin aceptar el estado como parámetro de entrada, y su test
  unitario.
  RF: RF-9
  Hecho cuando: `pytest -q -k estado_inicial` pasa, confirmando que el
  resultado siempre es "Activo".

## Fase 2 — Persistencia

- [x] **T09 — Modelo de datos y conexión a la base**
  Implementar `database.py` (engine + sesión SQLAlchemy sobre
  `app/backend/database.db`) y `models.py` (tabla `Customer`: DNI entero
  único, nombre, apellido, email, teléfono, estado enumerado con default
  "Activo").
  RF: RF-6, RF-9 (estructura de datos que los sostiene)
  Hecho cuando: un test o script mínimo ejecuta
  `Base.metadata.create_all(engine)` sobre una base SQLite temporal sin
  errores, y la columna DNI rechaza un `INSERT` duplicado por su constraint
  de unicidad.

- [x] **T10 — Schema de entrada del alta**
  Implementar en `schemas.py` el modelo Pydantic del payload de alta, con
  los 5 campos de entrada obligatorios.
  RF: RF-7
  Hecho cuando: instanciar el schema con un campo faltante lanza
  `ValidationError` mencionando ese campo específico.

- [x] **T11 — Detección de DNI duplicado en el repositorio**
  Implementar en `repository.py` la función que verifica si un DNI
  (normalizado) ya existe en la base, sin importar el estado del cliente
  existente, con tests de integración sobre una base SQLite temporal.
  RF: RF-6
  Hecho cuando: `pytest -q -k duplicado` pasa, cubriendo DNI exacto
  duplicado, DNI con cero a la izquierda duplicado, y duplicado contra un
  cliente existente en estado Inactivo.

- [x] **T12 — Inserción de cliente nuevo en el repositorio**
  Implementar en `repository.py` la función que inserta un cliente nuevo,
  usando `core.py` para asignar el estado inicial, con test de integración.
  RF: RF-1, RF-9
  Hecho cuando: `pytest -q -k insertar_cliente` pasa, verificando que el
  cliente queda persistido con estado "Activo".

## Fase 3 — API (`routes/clientes.py`)

- [x] **T13 — Endpoint: reporte de campos obligatorios faltantes**
  Implementar el endpoint de alta orquestando `schemas.py` para detectar
  campos vacíos y devolver todas las advertencias de obligatoriedad juntas.
  RF: RF-7, RF-8
  Hecho cuando: un `TestClient` de FastAPI, enviando el payload con los 5
  campos vacíos, recibe una respuesta con las 5 advertencias
  correspondientes.

- [x] **T14 — Endpoint: camino feliz**
  Completar el endpoint para que, con datos válidos y DNI no registrado,
  cree el cliente y devuelva el mensaje "Cliente registrado exitosamente".
  RF: RF-1
  Hecho cuando: `pytest -q -k alta_exitosa` pasa.

- [x] **T15 — Endpoint: múltiples errores de formato combinados**
  Integrar en el endpoint las validaciones de `core.py` (RF-2 a RF-5) de
  forma que, ante varios campos inválidos en un mismo envío, todas las
  advertencias de formato se devuelvan juntas.
  RF: RF-8
  Hecho cuando: `pytest -q -k multiples_errores` pasa, enviando un payload
  con nombre y teléfono inválidos a la vez y recibiendo ambas advertencias.

- [x] **T16 — Endpoint: bloqueo por DNI duplicado**
  Integrar en el endpoint la verificación de duplicado de `repository.py`,
  devolviendo la advertencia correspondiente sin crear el registro.
  RF: RF-6
  Hecho cuando: `pytest -q -k dni_duplicado_endpoint` pasa.

## Fase 4 — Script de datos ficticios

- [x] **T17 — Script de seed de clientes ficticios**
  Implementar `scripts/seed_clientes_ficticios.py` reutilizando `core.py` y
  `repository.py`, con el dataset propuesto en `plan.md`, de forma
  idempotente.
  RF: RF-1 a RF-7, RF-9 (indirecto, vía reutilización del núcleo)
  Hecho cuando: correr el script dos veces seguidas contra la misma base no
  duplica registros (el conteo de filas es igual después de la segunda
  corrida).

## Fase 5 — Frontend

- [x] **T18 — Cliente HTTP del alta**
  Implementar `api/clientesApi.js`: función que llama al endpoint de alta y
  traduce la respuesta a éxito o lista de errores por campo.
  RF: RF-1, RF-8
  Hecho cuando: un test con `fetch` mockeado confirma la forma de retorno
  esperada tanto para una respuesta de éxito como para una de error.

- [x] **T19 — Esqueleto del formulario**
  Implementar `ClienteForm.jsx` con los 5 campos de entrada y estado local
  (`useState`) por campo, documentado con JSDoc.
  RF: RF-1 (soporte estructural)
  Hecho cuando: `npm run typecheck` pasa sin errores y un test básico de
  React Testing Library confirma que el componente renderiza los 5 campos.

- [x] **T20 — Mostrar todas las advertencias de un intento**
  Conectar el envío del formulario a `clientesApi.js` y mostrar en pantalla
  todas las advertencias devueltas, una por campo.
  RF: RF-8
  Hecho cuando: un test de RTL con la API mockeada devolviendo 2 errores de
  campo distintos muestra ambos mensajes en pantalla.

- [x] **T21 — Conservar valores ingresados tras un error**
  Ajustar `ClienteForm.jsx` para que, ante una respuesta con advertencias,
  los valores ya ingresados no se borren.
  RF: RF-8
  Hecho cuando: un test de RTL confirma que, tras una respuesta de error
  simulada, los inputs conservan el texto ingresado por el usuario.

- [x] **T22 — Confirmación y limpieza tras alta exitosa**
  Ajustar `ClienteForm.jsx` para mostrar "Cliente registrado exitosamente" y
  vaciar todos los campos cuando la API responde éxito.
  RF: RF-1
  Hecho cuando: un test de RTL con la API mockeada devolviendo éxito
  confirma el mensaje en pantalla y que los 5 inputs quedan vacíos.

- [x] **T23 — Estilos responsivos**
  Aplicar layout responsivo (flexbox/grid + media queries) a
  `ClienteForm.jsx` para uso en plataformas móviles.
  RF: NFR — usabilidad móvil
  Hecho cuando: `npm run typecheck` pasa y una revisión manual en el
  navegador con el viewport en 375px de ancho muestra el formulario usable
  sin scroll horizontal.

## Fase 6 — Verificación final

- [x] **T24 — Verificación completa contra la matriz de trazabilidad**
  Revisar la matriz de trazabilidad de `plan.md` y confirmar que cada RF-1 a
  RF-10 tiene al menos un test en verde asociado.
  RF: RF-1 a RF-10 (verificación de cobertura total)
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada fila de la matriz de trazabilidad
  tiene un test correspondiente pasando.

## Fase 7 — Ajustes post-entrega (email con TLD + validación en Frontend)

- [x] **T25 — Email válido con TLD**
  Revertir la regla de `core.py`: el dominio del email ahora debe tener un
  punto (`usuario@dominio.tld`); actualizar los fixtures de email en todos
  los tests de backend y en el dataset del script de seed.
  RF: RF-3
  Hecho cuando: `pytest -q` pasa completo (36 tests), cubriendo
  "user@dominio.com" (válido) y "user@dominio" (ahora inválido).

- [x] **T26 — Módulo de validación en el Frontend**
  Crear `app/frontend/validation.js`, réplica en JavaScript de las reglas de
  `core.py` (obligatoriedad + formato de nombre/apellido, email, teléfono,
  DNI), con sus tests unitarios (sin renderizar componentes).
  RF: RF-2 a RF-5, RF-7, RF-11
  Hecho cuando: `npm run test -- validation` pasa, cubriendo campos vacíos,
  formato inválido de cada campo y un caso con varios errores a la vez.

- [x] **T27 — Bloquear el envío y mostrar carteles del Frontend**
  Integrar `validation.js` en `ClienteForm.jsx`: al enviar, validar primero
  en el Frontend; si hay errores de obligatoriedad o formato, mostrarlos de
  inmediato (mismo estilo de cartel que los errores del backend) y NO llamar
  a la API. Si la validación del Frontend pasa, continuar el flujo existente
  contra el backend (incluida la detección de DNI duplicado, que sigue
  siendo solo del servidor).
  RF: RF-11
  Hecho cuando: un test de RTL con formulario vacío confirma que se muestran
  las 5 advertencias y que `altaCliente` (la API) no se invoca; y otro test,
  con datos válidos para el Frontend pero rechazados por el backend (ej. DNI
  duplicado), confirma que la API sí se invoca y la advertencia se muestra
  igual.
