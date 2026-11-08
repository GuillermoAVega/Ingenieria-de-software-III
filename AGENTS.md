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

## Modularidad y responsabilidad única

Todo cambio nuevo y toda refactorización debe mantener el código modularizado, con la menor cantidad de código necesaria para resolver el problema.

### Frontend

- Las páginas deben coordinar la pantalla y renderizar; no deben contener reglas de negocio, llamadas HTTP ni transformaciones complejas.
- La lógica de estado, carga, validación y envío debe vivir en hooks propios de la feature.
- Las llamadas HTTP deben vivir en `api.ts` de la feature y usar `apiFetch` o el cliente compartido.
- Los componentes visuales reutilizables deben extraerse a archivos propios dentro de la feature o de `ui` cuando sean realmente compartidos.
- Los tipos y estados deben declararse junto a la feature que los usa; no duplicar tipos ni respuestas de API.
- Las funciones de formato, selección y transformación reutilizables deben extraerse a módulos pequeños, puros y testeables.
- No agregar componentes, hooks, estados, props, estilos ni funciones que no sean necesarios para el comportamiento solicitado.
- No mantener código de demostración, imports, variables ni ramas sin uso en funcionalidades reales.
- Una refactorización debe conservar el comportamiento existente; los cambios funcionales deben hacerse en un commit separado.

### Backend

- Los routers deben limitarse a recibir la petición, validar dependencias y delegar en servicios.
- Las reglas de negocio deben vivir en servicios del dominio y no repetirse entre routers.
- Los schemas definen contratos de entrada y salida; los modelos definen persistencia y relaciones.
- Las consultas reutilizables deben extraerse a servicios o repositorios pequeños cuando eviten duplicación.
- Cada módulo debe depender de contratos claros y evitar importar detalles internos de otra feature sin necesidad.
- No crear funciones genéricas o abstracciones prematuras: extraer solo cuando exista responsabilidad duplicada o una unidad de comportamiento clara.

### Forma de refactorizar

- Refactorizar por feature y en pasos pequeños.
- Antes de mover código, identificar qué responsabilidad se separa y mantener las interfaces públicas estables.
- Verificar cada paso con los tests correspondientes y, en Frontend, con `npx tsc -b --pretty false`.
- Revisar el diff para asegurar que el commit incluya solo la refactorización prevista.

## Frontend: estado y hooks

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
