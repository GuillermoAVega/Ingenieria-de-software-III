# Tasks 014 — Correcciones sobre Alta y Listado de Cliente

Tareas derivadas de `spec.md` y `plan.md`, en orden de dependencia. Cada
tarea es acotada (≈20-30 min) y su "Hecho cuando" debe poder verificarse
ejecutando un comando o una acción concreta.

## Fase 0 — Backend: repositorio

- [x] **T01 — `active_customer_exists_with_dni`**
  Agregar en `repository.py` la función que verifica si el DNI
  pertenece a un cliente en estado Activo (sin excluir ningún `id`),
  con sus tests de integración.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k active_customer_exists_with_dni` pasa,
  cubriendo un DNI de un cliente Activo (`True`), un DNI que solo
  pertenece a un cliente Inactivo (`False`), y un DNI inexistente
  (`False`).

## Fase 1 — Backend: endpoint

- [x] **T02 — Usar la nueva función en `alta_cliente`**
  Reemplazar `repository.dni_exists` por
  `repository.active_customer_exists_with_dni` en la ruta `POST
  /clientes`.
  [Cubre RF-1, RF-2]
  Hecho cuando: `pytest -q -k alta_cliente` pasa, cubriendo que un DNI
  de un cliente Activo sigue devolviendo 422 (RF-1), y que un DNI que
  solo pertenece a un cliente Inactivo ahora devuelve 201 (RF-2).

- [x] **T03 — El cliente Inactivo no se modifica tras el alta con su mismo DNI**
  [Cubre RF-2]
  Hecho cuando: un test de integración da de alta un cliente con el DNI
  de uno Inactivo, y confirma que el cliente Inactivo original
  conserva su nombre y su estado sin cambios, y que ambos clientes
  (`id` distintos) quedan persistidos con el mismo valor de DNI.

## Fase 2 — Frontend: texto de ayuda

- [x] **T04 — Texto de ayuda en `ClienteListado.jsx`**
  Agregar el párrafo "Podés buscar por Nombre, Apellido o DNI." debajo
  del formulario de búsqueda.
  [Cubre RF-3]
  Hecho cuando: `npm run test -- ClienteListado` pasa, confirmando que
  el texto está presente al renderizar el componente, antes de
  cualquier búsqueda.

## Fase 3 — Verificación final

- [x] **T05 — Verificación completa contra la matriz de trazabilidad**
  Revisar `plan.md` y confirmar que cada RF-1 a RF-3 tiene al menos un
  test en verde asociado.
  [Cubre RF-1 a RF-3]
  Hecho cuando: `pytest -q`, `npm run test` y `npm run typecheck`
  terminan sin errores ni tests saltados, y cada RF de la spec tiene un
  test correspondiente pasando.
