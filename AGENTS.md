# AGENTS.md — Propuesta productividad

## Proyecto
Página web dedicada a la venta de productos comerciales.
Backend con FastAPI + Pydantic + SQLAlchemy (`app/backend/core.py`).
Frontend con React + JavaScript + Vite (`app/frontend/main.jsx`).
Persistencia en base de datos SQLite local (`app/backend/database.db`).

## Comandos
- Tests backend: `pytest -q`
- Tests frontend: `npm run test` (Vitest)
- Verificar tipado frontend: `npm run typecheck` (JSDoc + `tsc --checkJs`)
- Instalar dependencias frontend: `npm install`

## Estilo
- Python 3.12+, type hints en todas las funciones públicas.
- Frontend en JavaScript (sin TypeScript); documentar tipos con JSDoc en funciones y componentes públicos.
- Identificadores en inglés; mensajes de usuario en español.
- Diseño apto para plataformas moviles.
- Commits en formato Conventional Commits, en español (ej. `feat(carrito): agregar validación de stock`).

## Reglas
- Lee `docs/constitution.md` y la spec activa en `specs/` antes de tocar código.
- No añadas dependencias ni cambies el formato de la base de datos sin actualizar antes la spec.
- No modifiques archivos dentro de `specs/` salvo petición explícita.

## Al terminar cualquier tarea
- Ejecuta `pytest -q` (backend), `npm run test` (frontend) y `npm run typecheck` (verificación de tipado JSDoc) y confirma en tu respuesta que todo pasa.
