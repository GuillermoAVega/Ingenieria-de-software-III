# Propuesta de Productividad

Página web para la gestión de clientes, productos y ventas de un
comercio: alta/baja/modificación/listado de clientes y productos, y
registro, modificación, cierre, anulación y listado de ventas.

## Stack

- **Backend:** Python 3.12+, FastAPI, Pydantic, SQLAlchemy, sobre SQLite
  (`app/backend/database.db`, se crea sola al arrancar).
- **Frontend:** React + JavaScript (sin TypeScript, tipado documentado
  con JSDoc), Vite, Vitest + React Testing Library.

## Requisitos previos

- Python 3.12 o superior
- Node.js 20 o superior (con `npm`)

## Instalación

### 1. Backend

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend

```bash
npm install
```

## Poner el proyecto en funcionamiento

Se necesitan dos procesos corriendo en paralelo (dos terminales).

**Terminal 1 — Backend** (con el entorno virtual activado):

```bash
source .venv/bin/activate
npm run backend
```

Sirve la API en `http://localhost:8000` (documentación interactiva en
`http://localhost:8000/docs`) y crea `app/backend/database.db` si no
existe todavía.

**Terminal 2 — Frontend:**

```bash
npm run dev
```

Sirve la aplicación en `http://localhost:5173`. Las rutas `/clientes`,
`/productos` y `/ventas` quedan proxeadas al backend (puerto 8000), así
que alcanza con abrir `http://localhost:5173` en el navegador.

> Si el backend no está corriendo, el frontend igual carga pero
> cualquier búsqueda o alta va a fallar (no hay a dónde proxear la
> petición).

### Reiniciar los datos

La base de datos es un único archivo SQLite. Para empezar de cero,
detené el backend y borrá `app/backend/database.db`; se vuelve a crear
vacía en el próximo arranque.

## Correr las pruebas

```bash
# Backend (pytest)
source .venv/bin/activate
pytest -q

# Frontend (Vitest)
npm run test

# Verificación de tipado del frontend (JSDoc vía tsc)
npm run typecheck
```

Las pruebas de backend usan una base SQLite en memoria (no tocan
`app/backend/database.db`), así que se pueden correr con el servidor
apagado o prendido, sin pisar datos reales.

## Estructura del proyecto

```
app/backend/     API FastAPI: modelos (models.py), repositorios y
                 rutas por dominio (cliente, producto, venta)
app/frontend/    App React: componentes, lógica de negocio pura
                 (testeable sin renderizar UI) y clientes de API
tests/backend/   Tests de pytest (unitarios + integración con TestClient)
tests/frontend/  Tests de Vitest + Testing Library
docs/            Constitución del proyecto (reglas y convenciones)
specs/           Especificaciones spec-driven (una carpeta por feature,
                 con spec.md/plan.md/tasks.md)
```

Cada feature del proyecto se desarrolló siguiendo el flujo documentado
en `specs/`: primero la especificación (`spec.md`), después el plan
técnico (`plan.md`) y el desglose en tareas (`tasks.md`), y recién
después la implementación. `docs/constitution.md` resume las reglas de
fondo (stack fijo, lógica de negocio separada de la UI, tests
obligatorios, etc.) y `AGENTS.md` los comandos y convenciones de
trabajo del día a día.
