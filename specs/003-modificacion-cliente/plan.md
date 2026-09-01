# Plan 003 — Modificación de Cliente

Plan técnico para implementar `specs/003-modificacion-cliente/spec.md`,
respetando `docs/constitution.md` y reutilizando lo ya construido en
[[001-alta-cliente]] y [[002-baja-cliente]] (`Customer`, `find_by_dni`,
`_normalize_payload`/`_validate_fields`/`_serialize_customer`,
`validation.js`, `clientesApi.js`). Este documento no contiene código:
describe estructura, decisiones y estrategia de verificación.

## Estructura de módulos

### Backend (`app/backend/`)

| Módulo | Responsabilidad | RF que cubre |
|---|---|---|
| `models.py` (modificado) | Quita el `unique=True` de la columna `dni` en `Customer` (mantiene `index=True` para la búsqueda). | RF-7 |
| `repository.py` (extendido) | `find_by_dni` ahora prioriza el resultado Activo cuando dos clientes comparten el mismo DNI. Agrega `dni_belongs_to_another_active_customer` (excluye al propio cliente, solo cuenta conflicto si el otro está Activo) y `update_customer` (actualiza DNI/nombre/apellido/email/teléfono, nunca `status`). | RF-1, RF-6, RF-7, RF-9, RF-11 |
| `routes/clientes.py` (extendido) | Agrega `PUT /clientes/{dni}/editar`, reutilizando `_normalize_payload`, `_validate_fields` y `_serialize_customer` ya definidos para el alta: 404 si el DNI de la URL no existe, 422 con advertencias si hay error de formato/obligatoriedad o si el nuevo DNI pertenece a otro cliente Activo, 200 con el mensaje de éxito y los datos actualizados si guarda. | RF-1 a RF-11 (orquesta todo el flujo) |

### Frontend (`app/frontend/`)

| Módulo | Responsabilidad | RF que cubre |
|---|---|---|
| `clienteFields.js` (nuevo) | Metadata compartida de los 5 campos del formulario (label, hint, inputMode), extraída de `ClienteForm.jsx` para que también la use `ClienteEdicionForm.jsx`. | RF-3, RF-4 |
| `clienteEdicion.js` (nuevo) | Módulo puro, sin dependencia de React: interpreta el resultado de la búsqueda para la edición (no encontrado / encontrado con sus datos actuales). | RF-1, RF-2 |
| `api/clientesApi.js` (extendido) | Agrega `editarCliente(dni, input)` (`PUT /clientes/{dni}/editar`), misma forma de traducción éxito/error que las funciones existentes. | RF-8, RF-9 |
| `components/ClienteEdicionForm.jsx` (nuevo) | Búsqueda por DNI (reutiliza `buscarCliente`) → formulario pre-cargado con los datos actuales → validación inmediata con `validation.js` → diálogo de confirmación → guarda con `editarCliente`. | RF-1 a RF-11 |
| `App.jsx` (extendido) | Agrega la pestaña "Editar Cliente" junto a las de Alta y Baja. | Estructural, sin RF directo |

## Decisiones técnicas

1. **Reutilizar el endpoint existente `GET /clientes/{dni}`** (de [[002-baja-cliente]]) para la búsqueda de RF-1/RF-2, sin crear un endpoint de búsqueda propio para la edición.
   Justificación: es exactamente la misma operación (localizar un cliente por DNI, informar si no existe); duplicarla no aportaría ningún comportamiento distinto.
   Alternativa descartada: un endpoint de búsqueda específico para edición — descartada por ser una copia idéntica de uno ya construido. *(RF-1, RF-2)*

2. **Quitar la restricción `unique=True` de la columna `dni`**, dejando la validación de unicidad exclusivamente en la capa de aplicación.
   Justificación: RF-7 exige permitir que el DNI editado coincida con el de otro cliente Inactivo, lo cual es incompatible con una unicidad global a nivel de base de datos. La regla real (RF-6: único solo entre Activos) pasa a `repository.dni_belongs_to_another_active_customer`, igual que el alta ya valida duplicados en la capa de aplicación (`repository.dni_exists`) sin depender del constraint de la base.
   Riesgo aceptado: una escritura SQL directa que bypasee `repository.py` podría crear dos clientes Activos con el mismo DNI sin que la base lo impida. Se acepta porque toda escritura de esta app ya pasa exclusivamente por `repository.py` (decisión vigente desde [[001-alta-cliente]]).
   Nota operativa: el stack no incluye una herramienta de migraciones (no hay Alembic, y agregarlo no está justificado por esta única feature — regla 1 de la constitución); este cambio de esquema requiere borrar el `database.db` de desarrollo existente para que se recree sin el constraint viejo la próxima vez que se levante el backend.
   Alternativa descartada: un índice único parcial a nivel SQLite (única entre filas con `status = 'Activo'`) — descartada por atar el modelo a sintaxis específica de un dialecto para un refuerzo que la validación de aplicación ya cubre. *(RF-6, RF-7)*

3. **`find_by_dni` prioriza el resultado Activo** cuando dos o más clientes comparten el mismo DNI, en vez de devolver el primero que encuentre sin criterio.
   Justificación: una vez que RF-7 permite DNIs compartidos con un Inactivo, la búsqueda (reutilizada por [[002-baja-cliente]] y por esta spec) debe resolver de forma determinística a qué cliente se refiere; priorizar el Activo es la lectura correcta porque solo puede existir un cliente Activo por DNI (RF-6 lo garantiza).
   Alternativa descartada: dejar el orden sin criterio explícito — descartada porque un mismo DNI podría devolver un cliente distinto en cada consulta. *(RF-1, RF-7)*

4. **Nueva función `dni_belongs_to_another_active_customer(session, dni, exclude_id)`**, separada de `dni_exists` (que el alta sigue usando sin cambios).
   Justificación: son dos reglas de negocio distintas — el alta bloquea contra cualquier estado (RF-6 de [[001-alta-cliente]]); la edición solo bloquea contra otro cliente Activo y excluye al propio cliente editado (RF-6/RF-7 de esta spec). Mezclarlas en una función con flags opcionales sería más confuso que dos funciones con nombres explícitos.
   Alternativa descartada: parametrizar `dni_exists` con `exclude_id`/`only_active` — descartada por oscurecer qué regla aplica en cada caso. *(RF-6, RF-7)*

5. **El endpoint de edición reutiliza `_normalize_payload`, `_validate_fields` y `_serialize_customer`** ya definidos en `routes/clientes.py` para el alta, en vez de duplicar esa lógica.
   Justificación: RF-4 exige exactamente las mismas reglas de formato, obligatoriedad y recorte que el alta; reutilizar las mismas funciones garantiza que ambas features nunca diverjan por error humano.
   Alternativa descartada: copiar la lógica de validación en un módulo nuevo — descartada por duplicar código que ya cumple RF-4 al pie de la letra. *(RF-4, RF-5)*

6. **El endpoint de edición usa el DNI de la URL** (`PUT /clientes/{dni}/editar`, el mismo DNI usado en la búsqueda de RF-1) para localizar al cliente, en vez de introducir el `id` interno de la base como identificador expuesto por la API.
   Justificación: mantiene el mismo patrón de URL que `PATCH /clientes/{dni}/baja` de [[002-baja-cliente]]; combinada con la decisión técnica 3 (prioridad al Activo), la resolución del DNI de la URL es consistente entre la búsqueda y el guardado, bajo el mismo supuesto de un único Administrador operando que ya aceptó RF-8 de [[002-baja-cliente]].
   Alternativa descartada: exponer el `id` interno del cliente como clave de la URL de edición — descartada por romper la convención de URLs basadas en DNI del resto de la API, sin necesidad real dado que la decisión técnica 3 ya resuelve la ambigüedad. *(RF-1, RF-6, RF-7, RF-8, RF-9)*

7. **El Frontend reutiliza `validation.js` (`validateClienteForm`) para dar feedback inmediato** en el formulario de edición, igual que en `ClienteForm.jsx`, aunque la spec no lo exige de forma explícita.
   Justificación: RF-4 exige las mismas reglas que el alta, que ya da ese feedback inmediato; reutilizar el módulo existente no cuesta código nuevo y evita una experiencia inconsistente entre dar de alta y editar. El backend (`PUT /clientes/{dni}/editar`) sigue siendo la autoridad final ante cualquier Frontend desactualizado o baipaseado.
   Alternativa descartada: no validar nada en el Frontend y depender solo de la respuesta del backend — descartada por empeorar la experiencia sin ningún beneficio, dado que la lógica ya existe y está probada. *(RF-4, RF-5)*

8. **Los campos editables se extraen a `clienteFields.js`**, compartido por `ClienteForm.jsx` (alta) y `ClienteEdicionForm.jsx` (edición), en vez de duplicar el array `FIELDS`.
   Justificación: ambos formularios comparten los mismos 5 campos con las mismas reglas (RF-4); mantener dos copias es una fuente de divergencia accidental.
   Alternativa descartada: copiar el array `FIELDS` dentro de `ClienteEdicionForm.jsx` — descartada por duplicar información que ya vive en `ClienteForm.jsx`. *(RF-3, RF-4)*

9. **Tras un guardado exitoso, `ClienteEdicionForm.jsx` vuelve al estado de búsqueda** (limpia el DNI buscado y oculta el formulario), igual que `ClienteBajaForm.jsx` tras una baja exitosa.
   Justificación: mantiene el mismo patrón de interacción ya usado en [[002-baja-cliente]] para cerrar el ciclo de una operación completada, en vez de un tercer comportamiento distinto entre las tres features de cliente.
   Alternativa descartada: dejar el formulario abierto con los valores recién guardados — descartada por no estar pedida y por romper la consistencia entre features. *(RF-9)*

## Estrategia de tests

### Backend — `test_database.py` (esquema)
- Se elimina `test_dni_unico_rechaza_duplicado` (ya no refleja el comportamiento deseado tras la decisión técnica 2).
- Se agrega `test_dni_no_es_unico_a_nivel_de_base`: insertar dos clientes con el mismo DNI ya no lanza `IntegrityError`, documentando la relajación de forma explícita. *(RF-7)*

### Backend — tests de integración sobre `repository.py` (SQLite temporal)
- `find_by_dni` devuelve el cliente Activo cuando existe un Activo y un Inactivo con el mismo DNI. *(RF-1, RF-7)*
- `dni_belongs_to_another_active_customer`: `True` contra otro cliente Activo con ese DNI; `False` contra el propio cliente (excluido por `exclude_id`); `False` contra otro cliente Inactivo con ese DNI; `False` si nadie tiene ese DNI. *(RF-6, RF-7)*
- `update_customer` actualiza los 5 campos y conserva el `status` previo, probado tanto para un cliente Activo como para uno Inactivo. *(RF-9, RF-11)*

### Backend — tests de integración sobre `routes/clientes.py` (`TestClient`)
- Edición exitosa sobre un cliente Activo: 200, mensaje de éxito, datos actualizados, `status` sigue Activo. *(RF-9)*
- Edición exitosa sobre un cliente Inactivo: 200, datos actualizados, `status` sigue Inactivo. *(RF-3, RF-9, RF-11)*
- Edición sin cambiar el DNI: no dispara advertencia de duplicado contra sí mismo. *(RF-6)*
- Edición con campos vacíos y/o de formato inválido combinados: 422 con todas las advertencias en el mismo intento; una búsqueda posterior confirma que no cambió nada. *(RF-4, RF-5)*
- Edición con DNI que pertenece a otro cliente Activo: 422 "El DNI ya está en uso"; una búsqueda posterior confirma que no cambió nada, ni siquiera los demás campos válidos del intento. *(RF-6)*
- Edición con DNI que pertenece a otro cliente Inactivo: 200, se guarda igual. *(RF-7)*
- Edición sobre un DNI que no existe: 404. *(RF-2)*
- `GET /clientes/{dni}` cuando un cliente Activo y uno Inactivo comparten DNI: devuelve el Activo. *(RF-1, soporta la búsqueda reutilizada)*

### Frontend — tests unitarios sobre `clienteEdicion.js` (sin React)
- Resultado "no encontrado" → estado `NOT_FOUND`. *(RF-2)*
- Cliente encontrado → estado `FOUND` con sus datos. *(RF-1, RF-3)*

### Frontend — tests sobre `clientesApi.js` (fetch mockeado)
- `editarCliente`: traduce una respuesta 200 y una 422 a la forma esperada. *(RF-8, RF-9)*

### Frontend — Vitest + React Testing Library sobre `ClienteEdicionForm.jsx`
Con `clientesApi.js` mockeado (sin red real):
- Buscar un DNI inexistente: se muestra el mensaje de "no encontrado" y no se renderiza el formulario de edición. *(RF-2)*
- Buscar un DNI existente: se renderiza el formulario pre-cargado con los 5 valores actuales. *(RF-1, RF-3)*
- Enviar con un campo inválido o vacío: se muestran las advertencias correspondientes de inmediato, no aparece el diálogo de confirmación y `editarCliente` no se invoca. *(RF-4, RF-5)*
- Enviar con datos válidos: aparece el diálogo de confirmación con "Confirmar"/"Cancelar", sin invocar `editarCliente` todavía. *(RF-8)*
- Click en "Confirmar": se invoca `editarCliente`, se muestra "Cliente modificado exitosamente" y el formulario vuelve al estado de búsqueda. *(RF-9)*
- Click en "Cancelar": NO se invoca `editarCliente`; los valores editados permanecen en el formulario. *(RF-10)*
- El backend rechaza el guardado por DNI duplicado (tras confirmar): se muestra "El DNI ya está en uso" y se conservan los valores para poder corregir y reintentar. *(RF-6)*

### Verificación de tipado
`npm run typecheck` se ejecuta como parte del pipeline de verificación de cada tarea, igual que en las features anteriores.

## Matriz de trazabilidad

| Requisito | Módulo(s) que lo implementa | Test(s) que lo cubre |
|---|---|---|
| RF-1 | `repository.py` (`find_by_dni`), `routes/clientes.py` (`GET`, reutilizado), `clienteEdicion.js`, `ClienteEdicionForm.jsx` | test de `find_by_dni` con DNI compartido; test de `ClienteEdicionForm` de búsqueda exitosa |
| RF-2 | `routes/clientes.py` (`GET`, reutilizado), `clienteEdicion.js`, `ClienteEdicionForm.jsx` | test de `clienteEdicion.js` NOT_FOUND; test de `ClienteEdicionForm` "no encontrado" |
| RF-3 | `ClienteEdicionForm.jsx`, `clienteFields.js` | test de integración de edición sobre cliente Inactivo; test de `ClienteEdicionForm` de formulario pre-cargado |
| RF-4 | `routes/clientes.py` (`_normalize_payload`/`_validate_fields`, reutilizados), `validation.js` (reutilizado) | test de integración de campos inválidos/vacíos; test de `ClienteEdicionForm` de validación inmediata |
| RF-5 | `routes/clientes.py` | test de integración de múltiples errores combinados |
| RF-6 | `repository.py` (`dni_belongs_to_another_active_customer`), `routes/clientes.py` (`PUT`) | test de `dni_belongs_to_another_active_customer`; test de integración de DNI duplicado contra Activo; test de `ClienteEdicionForm` de rechazo tras confirmar |
| RF-7 | `models.py` (sin `unique`), `repository.py` (`find_by_dni`, `dni_belongs_to_another_active_customer`) | `test_dni_no_es_unico_a_nivel_de_base`; test de integración de DNI duplicado contra Inactivo (permitido) |
| RF-8 | `ClienteEdicionForm.jsx` | test de `ClienteEdicionForm` de aparición del diálogo de confirmación |
| RF-9 | `repository.py` (`update_customer`), `routes/clientes.py` (`PUT`), `clientesApi.js` (`editarCliente`), `ClienteEdicionForm.jsx` | test de `update_customer`; test de integración de edición exitosa; test de `ClienteEdicionForm` de confirmación |
| RF-10 | `ClienteEdicionForm.jsx` | test de `ClienteEdicionForm` de cancelación |
| RF-11 | `repository.py` (`update_customer`, no toca `status`) | test de `update_customer` sobre cliente Activo e Inactivo; test de integración de edición sobre Inactivo |

## Cumplimiento de la constitución

- **Regla 1 (stack fijo)**: se reutiliza FastAPI + Pydantic + SQLAlchemy y React + JavaScript + JSDoc, sin agregar dependencias (se descartó explícitamente Alembic y un índice parcial específico de SQLite; ver decisión técnica 2).
- **Regla 2 (spec antes que código)**: este plan se redacta a partir de `specs/003-modificacion-cliente/spec.md`, ya aprobada.
- **Regla 3 (lógica separada de la interfaz)**: `clienteEdicion.js` concentra la interpretación de la búsqueda y es testeable sin renderizar React; `validation.js` (reutilizado) sigue cumpliendo el mismo rol para las reglas de formato.
- **Regla 4 (tests obligatorios)**: la estrategia de tests cubre los once RF de la spec, incluida la relajación de unicidad de RF-7, antes de considerar la feature terminada.
- **Regla 5 (persistencia única)**: la edición se aplica exclusivamente sobre `Customer` vía `repository.py`/`database.py`; no hay estado ad-hoc nuevo.
- **Regla 6 (idioma consistente)**: identificadores en inglés (`update_customer`, `dni_belongs_to_another_active_customer`, `ClienteEdicionForm.jsx`); mensajes al Administrador en español ("Cliente modificado exitosamente", "El DNI ya está en uso").
