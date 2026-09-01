# Tasks 015 — Texto de Ayuda en Listar Productos

Tareas derivadas de `spec.md` y `plan.md`. Cada tarea es acotada
(≈20-30 min) y su "Hecho cuando" debe poder verificarse ejecutando un
comando o una acción concreta.

## Fase 0 — Frontend

- [x] **T01 — Texto de ayuda en `ProductoListado.jsx`**
  Agregar el párrafo "Podés buscar por Nombre o Código/SKU." debajo del
  formulario de búsqueda, con su clase de estilo en
  `ProductoListado.css`.
  [Cubre RF-1]
  Hecho cuando: `npm run test -- ProductoListado` pasa, confirmando que
  el texto está presente al renderizar el componente, antes de
  cualquier búsqueda.

## Fase 1 — Verificación final

- [x] **T02 — Verificación completa**
  [Cubre RF-1]
  Hecho cuando: `npm run test` y `npm run typecheck` terminan sin
  errores ni tests saltados.
