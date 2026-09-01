# Tasks 003 — Modificación de Cliente

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Esquema: relajar la unicidad de DNI

- [x] **T01 — Quitar `unique=True` de `dni` en `models.py`**
  Actualizar `test_database.py`: eliminar `test_dni_unico_rechaza_duplicado`
  y agregar `test_dni_no_es_unico_a_nivel_de_base`, que inserta dos clientes
  con el mismo DNI y confirma que no lanza `IntegrityError`.
  RF: RF-7
  Hecho cuando: `pytest -q tests/backend/test_database.py` pasa con el
  nuevo test y sin el viejo.

## Fase 1 — Backend: repositorio

- [x] **T02 — `find_by_dni` prioriza el cliente Activo**
  Ajustar `find_by_dni` para que, ante DNIs compartidos, devuelva el cliente
  Activo antes que cualquier Inactivo, con test de integración.
  RF: RF-1, RF-7
  Hecho cuando: `pytest -q -k find_by_dni_prioriza` pasa, insertando un
  cliente Activo y uno Inactivo con el mismo DNI y verificando cuál devuelve
  la búsqueda.

- [x] **T03 — `dni_belongs_to_another_active_customer`**
  Implementar la función en `repository.py`, con tests de integración.
  RF: RF-6, RF-7
  Hecho cuando: `pytest -q -k dni_belongs_to_another_active` pasa, cubriendo
  otro cliente Activo (`True`), el propio cliente excluido (`False`), otro
  cliente Inactivo (`False`) y ningún cliente con ese DNI (`False`).

- [x] **T04 — `update_customer`**
  Implementar la función en `repository.py` (actualiza dni/nombre/apellido/
  email/teléfono, nunca `status`), con tests de integración.
  RF: RF-9, RF-11
  Hecho cuando: `pytest -q -k update_customer` pasa, verificando que el
  `status` no cambia tanto para un cliente Activo como para uno Inactivo.

## Fase 2 — Backend: endpoint de edición

- [x] **T05 — Endpoint `PUT /clientes/{dni}/editar`: camino feliz y no encontrado**
  Implementar el endpoint reutilizando `_normalize_payload`,
  `_validate_fields` y `_serialize_customer`; cubre edición exitosa y DNI
  inexistente (404).
  RF: RF-1, RF-2, RF-9
  Hecho cuando: `pytest -q -k editar_cliente_endpoint` pasa para ambos
  casos.

- [x] **T06 — Endpoint: reporte combinado de errores de formato/obligatoriedad**
  Cubrir en el endpoint el caso de múltiples campos inválidos/vacíos a la
  vez, sin guardar ningún cambio.
  RF: RF-4, RF-5
  Hecho cuando: un test de integración con dos campos inválidos a la vez
  recibe ambas advertencias y una búsqueda posterior confirma que no cambió
  nada.

- [x] **T07 — Endpoint: DNI duplicado contra Activo bloquea, contra Inactivo permite**
  Integrar `dni_belongs_to_another_active_customer` en el endpoint.
  RF: RF-6, RF-7
  Hecho cuando: `pytest -q -k dni_en_uso` pasa para el caso bloqueado
  (Activo) y `pytest -q -k dni_duplicado_inactivo_permitido` pasa para el
  caso permitido (Inactivo).

## Fase 3 — Frontend: reutilización y módulos puros

- [x] **T08 — Extraer `clienteFields.js` desde `ClienteForm.jsx`**
  Mover el array `FIELDS` a un módulo compartido; actualizar `ClienteForm.jsx`
  para consumirlo desde ahí, sin cambiar su comportamiento.
  RF: — (refactor de reutilización, base de RF-3/RF-4)
  Hecho cuando: `npm run test` y `npm run typecheck` siguen en verde sin
  ningún cambio en los tests existentes de `ClienteForm`.

- [x] **T09 — `clienteEdicion.js`**
  Implementar el módulo puro que interpreta el resultado de la búsqueda
  (no encontrado / encontrado), con tests unitarios sin React.
  RF: RF-1, RF-2
  Hecho cuando: `npm run test -- clienteEdicion` pasa, cubriendo ambos
  estados.

- [x] **T10 — `editarCliente` en `clientesApi.js`**
  Implementar la función de comunicación con el endpoint de edición, con
  tests con `fetch` mockeado.
  RF: RF-8, RF-9
  Hecho cuando: `npm run test -- clientesApi` pasa, cubriendo una respuesta
  200 y una 422.

## Fase 4 — Frontend: componente de edición

- [x] **T11 — Esqueleto de `ClienteEdicionForm.jsx`: búsqueda y formulario pre-cargado**
  Input de DNI + botón de búsqueda; al encontrar un cliente, mostrar el
  formulario con sus 5 valores actuales (usando `clienteFields.js`); al no
  encontrarlo, mostrar el mensaje de `clienteEdicion.js`.
  RF: RF-1, RF-2, RF-3
  Hecho cuando: un test de RTL confirma ambos casos (formulario pre-cargado
  / mensaje de no encontrado).

- [x] **T12 — Validación inmediata antes de confirmar**
  Integrar `validation.js`: al enviar el formulario, si hay errores de
  formato/obligatoriedad, mostrarlos de inmediato sin mostrar el diálogo de
  confirmación ni llamar a `editarCliente`.
  RF: RF-4, RF-5
  Hecho cuando: un test de RTL con un campo inválido confirma las
  advertencias y que `editarCliente` no fue invocada.

- [x] **T13 — Diálogo de confirmación y guardado**
  Mostrar el diálogo de confirmación cuando el formulario es válido; al
  confirmar, invocar `editarCliente`, mostrar "Cliente modificado
  exitosamente" y volver al estado de búsqueda.
  RF: RF-8, RF-9
  Hecho cuando: un test de RTL confirma la aparición del diálogo y otro
  confirma el guardado exitoso tras "Confirmar".

- [x] **T14 — Cancelar confirmación y error de DNI duplicado**
  Implementar "Cancelar" (cierra el diálogo, no llama a la API, conserva los
  valores) y el manejo del error 422 de DNI duplicado devuelto tras
  confirmar (muestra "El DNI ya está en uso", conserva los valores).
  RF: RF-6, RF-10
  Hecho cuando: dos tests de RTL cubren ambos casos por separado.

## Fase 5 — Integración de navegación

- [x] **T15 — Pestaña "Editar Cliente" en `App.jsx`**
  Agregar la tercera pestaña junto a Alta y Baja.
  RF: — (estructural)
  Hecho cuando: `npm run typecheck` pasa y una revisión manual permite
  alternar entre las tres vistas.

## Fase 6 — Verificación final

- [x] **T16 — Verificación completa contra la matriz de trazabilidad**
  Revisar la matriz de trazabilidad de `plan.md` y confirmar que cada RF-1 a
  RF-11 tiene al menos un test en verde asociado.
  RF: RF-1 a RF-11 (verificación de cobertura total)
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck` terminan
  sin errores ni tests saltados, y cada fila de la matriz de trazabilidad
  tiene un test correspondiente pasando.
