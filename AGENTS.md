# AGENTS.md

Guía general para agentes que modifiquen este repositorio.

## Alcance

Este archivo contiene reglas globales del repositorio. Las reglas específicas de cada parte viven en:

- `Backend/AGENTS.md` — FastAPI, SQLAlchemy, Pydantic, pruebas y base de datos.
- `Frontend/AGENTS.md` — React, TypeScript, estado, hooks, componentes y estilos.

Antes de trabajar en una de esas carpetas, leer también su `AGENTS.md`.

## Estructura

- `Backend/`: FastAPI + SQLAlchemy + Pydantic + SQLite.
- `Frontend/`: React 19 + TypeScript + Vite.
- `openspec/specs/`: especificaciones vigentes.
- `openspec/changes/`: cambios propuestos y archivo histórico.

## Especificaciones

- `openspec/specs/` es la fuente de verdad del comportamiento esperado.
- Los cambios de comportamiento deben reflejarse en `openspec/changes/` según el flujo de OpenSpec.
- Si el código y la especificación difieren, revisar la especificación antes de dar por correcta una implementación.

## Convenciones globales

- Mantener los textos visibles para el usuario (interfaz y mensajes de error) en español.
- Respetar la estructura, el nombrado y los patrones del área que se modifica.
- No agregar dependencias nuevas sin necesidad y sin actualizar el archivo de dependencias correspondiente.
- Tratar archivos y cambios desconocidos como trabajo del usuario: investigar antes de borrar o sobrescribir.
- No commitear archivos generados, secretos ni bases de datos locales (`node_modules/`, `dist/`, `venv/`, `__pycache__/`, `.env`, `*.db`).

## Verificación

Antes de cerrar un cambio, ejecutar la verificación del área modificada:

- Backend: `pytest` desde `Backend/`.
- Frontend: `npm run build` y `npx eslint <ruta>` desde `Frontend/`.
